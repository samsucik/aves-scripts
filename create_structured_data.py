from datetime import timedelta
import datetime
import json
import requests
import pytz
import re
from thefuzz import fuzz
import unicodedata
import gpxpy
import argparse
from PyInquirer import prompt
import pandas as pd

from aves_data import sky_condition_levels, wind_levels, temperature_levels, observation_characteristics
import bird_species

name_sim_threshold = 50


def get_dict_subset(dct, keys):
    return dict((key, dct[key]) for key in keys)


def get_default_observation_method(text):
    for word in ["ozyva", r"vola[^v]", "spieva"]:
        if re.search(word, text):
            return {"name": "AKUSTICKY MONITORING - akustický monitoring", "code": "15"}
    return {"name": "VIZUAL - vizuálne pozorovanie", "code": "8"}


def get_temperature_level(temp, temperature_levels):
    if temp is not None:
        for i, level in enumerate(temperature_levels[1:]):  # skip first option (N/A)
            if temp < max(level["range"]) and temp >= min(level["range"]):
                return i, get_dict_subset(level, ["name", "code"])

    return 0, None


def get_default_observation_characteristic(month, day):
    if month >= 4 and month < 8:
        return {"name": "A0 - výskyt od 1.4. do 31.7.", "code": "19"}
    elif month in [12, 1] or (month == 2 and day <= 15):
        return {"name": "ZIMOVANIE - zimovanie", "code": "70"}
    return {"name": "M_MV - migrácia alebo výskyt v mimohniezdnom období", "code": "36"}


def strip_accents(s):
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )


def get_similarity_score(texts, targets):
    def _sim_func(text1, text2):
        return fuzz.partial_ratio(text1, text2)

    if type(texts) == str:
        texts = [texts]
    if type(targets) == str:
        targets = [targets]

    score = max([_sim_func(text, target) for text in texts for target in targets])
    return score


def get_weather_level(text, weather_level_data):
    scores = {}

    for i, level_data in enumerate(weather_level_data):
        descriptive_words = level_data["descriptive_words"]
        score = get_similarity_score(text.lower(), descriptive_words)
        scores[i] = score

    top_result_idx = max(scores, key=scores.get)

    return top_result_idx, get_dict_subset(
        weather_level_data[top_result_idx], ["name", "code"])


def get_bird_names(text, species, n):
    candidates = []
    max_n_records = max(species_data["n_records"] for species_data in species)

    for species_data in species:
        names = []
        if species_data["name_sk"] is not None:
            names.append(species_data["name_sk"])
        if species_data["name_lat"] is not None:
            names.append(
                bird_species.remove_citation_from_scientific_name(
                    species_data["name_lat"]))

        # similarity with full name
        sim_full = max(fuzz.partial_ratio(
            strip_accents(text).lower(), strip_accents(name).lower()) for name in names
        )

        # similarity with parts of name
        sim_partial = []
        for name in names:
            for part in strip_accents(name).lower().strip().split(" "):
                sim_partial.append(
                    fuzz.partial_ratio(strip_accents(text).lower(), part)
                )
        sim_partial = max(sim_partial)

        max_sim = max(sim_full, sim_partial)
        if max_sim > name_sim_threshold:
            # max_sim is between name_sim_threshold and 100, we reward with up to 5
            # additional points species with lots of records in the Aves database
            score = max_sim + 5 * species_data["n_records"] / max_n_records
            candidates.append(
                {"score": score, "name": names[0], "species_id": species_data["species_id"]})

    if len(candidates) > 0:
        candidates.sort(key=lambda t: t["score"], reverse=True)

    # remove scores (used only for ordering the species)
    candidates = [get_dict_subset(cand, ["name", "species_id"]) for cand in candidates]

    return candidates[:n]


def get_secrets():
    with open("secrets.json") as f:
        return json.load(f)


def get_numbers_from_text(text):
    matches = re.findall(r"\d+(?=x)", text)
    if not matches:
        matches = re.findall(r"(?<![:0-9/.])\d+(?![:0-9/.])", text)
        if not matches:
            return [1]
    return [int(m) for m in matches]


def get_datetime_from_text(text):
    time_matches = re.findall(r"\d{1,2}:\d{1,2}", text)
    if len(time_matches) > 2 or not time_matches:
        print(f"Can't extract time(s) from text: '{text}'")
        return None

    duration = None
    hour = int(time_matches[0].split(":")[0])
    minute = int(time_matches[0].split(":")[1])
    if len(time_matches) == 2:
        duration = timedelta(
            hours=int(time_matches[1].split(":")[0]) - hour,
            minutes=int(time_matches[1].split(":")[1]) - minute,
        )

    date_matches = re.findall(r"\d{1,2}\.\d{1,2}(?=\.)|\d{1,2}/\d{1,2}", text)
    if len(date_matches) != 1:
        print(f"Can't extract date from text: '{text}'")
        return None
    date_match = date_matches[0]
    date_sep = "/" if "/" in date_match else "."
    day = int(date_match.split(date_sep)[0])
    month = int(date_match.split(date_sep)[1])

    return (day, month, hour, minute, duration)


def is_summer_time(year, month, day):
    dt = datetime.datetime(year, month, day)
    timezone = pytz.timezone("Europe/Bratislava")
    timezone_aware_date = timezone.localize(dt, is_dst=None)
    return timezone_aware_date.tzinfo._dst.seconds != 0


def get_temperature(api_key, year, month, day, hour, minute, duration, lat, lon, mock):
    if mock:
        return -30
    # +1h (CET) + 1h (if daylight saving applies)
    hour_adjustment = timedelta(
        hours=1 + (1 if is_summer_time(year, month, day) else 0)
    )

    start_timestamp = (
        datetime.datetime(year, month, day, hour=hour, minute=minute) - hour_adjustment
    ).timestamp()
    end_timestamp = (
        datetime.datetime(year, month, day, hour=hour, minute=minute)
        + duration
        - hour_adjustment
    ).timestamp()

    mid_timestamp = int((start_timestamp + end_timestamp) / 2)
    url = f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&dt={mid_timestamp}&appid={api_key}&units=metric"
    try:
        x = requests.get(url)
        if x.status_code == 200:
            return x.json()["data"][0]["temp"]
    except Exception:
        return None


def get_args():
    parser = argparse.ArgumentParser(
        description="Convert GPX waypoint data into JSON data."
    )
    parser.add_argument(
        "-i",
        "--input_file",
        type=str,
        help="The GPX file to process",
        required=True)
    parser.add_argument(
        "-o",
        "--output_file",
        type=str,
        help="The output JSON file name",
        required=True)
    parser.add_argument(
        "--mock",
        type=bool,
        help="Whether to mock API calls",
        default=False)
    return parser.parse_args()


def get_raw_data(input_file):
    data = []

    with open(input_file, "r") as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        for waypoint in gpx.waypoints:
            data.append(
                {
                    "text": waypoint.name,
                    "lat": waypoint.latitude,
                    "lon": waypoint.longitude,
                }
            )
    return data


def let_user_choose_option(name, options, default_idx):
    question = {
        "type": "list",
        "name": "value",
        "message": f"Choose {name}:",
        "choices": [{"name": option["name"], "value": i} for i, option in enumerate(options)],
        "default": default_idx
    }
    answer = prompt.prompt([question])
    return options[answer["value"]]


def let_user_search_for_species(species_all, observation_text):
    choices = []
    for i, species in enumerate(species_all):
        if species["name_sk"] and species["name_lat"]:
            name = f"{species['name_sk'].strip()} - {species['name_lat'].strip()}"
        else:
            name = species["name_sk"].strip() if species["name_sk"] else species[
                "name_lat"].strip()
        name_for_search = strip_accents(name).lower()

        # sort species by:
        # - match against record text (species names split on whitespace, without parenthesised parts)
        # - frequency of the species' observations
        name_parts = [strip_accents(part.strip().lower()) for part in bird_species.remove_citation_from_scientific_name(
            name).split() if len(part.strip()) > 2]
        text_match = get_similarity_score(name_parts, observation_text)
        score = species["freq_rank"] + 2 * text_match / 100

        choices.append({
            "name": name,
            "name_for_search": name_for_search,
            "value": i,
            "ordering_score": score
        })

    choices = sorted(choices, key=lambda s: s["ordering_score"], reverse=True)

    question = {
        "type": "searchable_menu",
        "name": "value",
        "message": "Choose species (type to filter):",
        "choices": choices
    }
    answer = prompt.prompt([question])
    return species_all[answer["value"]] if answer != {} else None


def let_user_enter_number(default, message="How many?"):
    age_mapping = {
        "a": "add",
        "s": "sad",
        "j": "juv",
        "i": "imm",
        "p": "pull"
    }
    sex_mapping = {
        "m": "male",
        "f": "female",
    }

    def _extract_numbers_from_answer(a):
        parts = a.split(",")
        result = {}
        for part in parts:
            part = part.strip()
            if part == "":
                continue
            ages = [
                age_val for age_key,
                age_val in age_mapping.items() if age_key in part]
            assert len(ages) in [0, 1], f"can't extract one age category from '{part}'"
            sexes = [
                sex_val for sex_key,
                sex_val in sex_mapping.items() if sex_key in part]
            assert len(sexes) in [0, 1], f"can't extract one sex category from '{part}'"

            numbers = re.findall(r"\d+", part)
            assert len(numbers) == 1, f"can't extract one number from '{part}'"
            number = int(numbers[0])

            if "o" in part:
                result["other"] = number
                continue

            if len(ages) + len(sexes) == 0:
                result["overall"] = number
            else:
                category = (sexes[0] if len(sexes) > 0 else "") + \
                    (ages[0] if len(ages) > 0 else "")
                result[category] = number

        if "overall" not in result:
            result["overall"] = sum(result.values())
        if "other" in result:
            del result["other"]

        return result

    question = {
        "type": "input",
        "name": "value",
        "message": message,
        "default": str(default),
        "filter": _extract_numbers_from_answer
    }
    answer = prompt.prompt([question])
    return answer["value"]


def let_user_enter_note(message="Note (optional):"):
    question = {
        "type": "input",
        "name": "value",
        "message": message
    }
    answer = prompt.prompt([question])
    return answer["value"]


def let_user_search_for_option(name, options, default_code, show_all=False):
    choices = []
    for option in options:
        choices.append({
            "name": option["name"],
            "name_for_search": strip_accents(option["name"]).lower(),
            "value": option["code"]
        })
    question = {
        "type": "searchable_menu",
        "name": "value",
        "message": f"Choose {name} (type to filter):",
        "choices": choices,
        "default": default_code,
    }
    kwargs = {"n_rows_to_show": len(options)} if show_all else {}
    answer = prompt.prompt([question], **kwargs)
    return [o for o in options if o["code"] == answer["value"]][
        0] if answer != {} else None


def let_user_search_for_land_structure(df):
    choices = []
    for i, land_struct_type in df.iterrows():
        children = df[df["position"].str.match(f"{land_struct_type['position']}([0-9]+\.)+")]
        children_names = [ch["name"] for _, ch in children.iterrows()]
        all_names_for_search = [land_struct_type["name"]] + children_names
        if pd.notna(land_struct_type["synonyms"]):
            all_names_for_search.append(land_struct_type["synonyms"])
        name_for_search = strip_accents(
            ", ".join(all_names_for_search)).lower()
        depth = land_struct_type["position"].count(".")
        choices.append({
            "name": " " * (depth - 1) + land_struct_type["name"],
            "name_for_search": name_for_search,
            "value": i
        })
    question = {
        "type": "searchable_menu",
        "name": "value",
        "message": "Choose land structure type (type to filter):",
        "choices": choices,
        "strip_answer": True
    }
    answer = prompt.prompt([question])
    return int(dict(df.iloc[answer["value"]])["code"]) if answer != {} else None


def create_result_from_raw_data(data_obj, year, species_list, land_structures_list,
                                temperature_api_key):
    text = data_obj["text"]
    lat = data_obj["lat"]
    lon = data_obj["lon"]

    geo_str = f"POINT({lon} {lat})"

    print(f"===== {text} ======")

    dt = get_datetime_from_text(text)
    if dt is None:
        return None

    day, month, hour, minute, duration = dt
    if duration is None:
        duration = timedelta(minutes=2)
    print(f"{day}.{month}.{year} {hour}:{minute} ({duration})")
    dt_to = datetime.datetime(year, month, day, hour=hour, minute=minute) + duration
    hour_to = dt_to.hour
    minute_to = dt_to.minute

    idx, sky_condition_level = get_weather_level(
        text, sky_condition_levels
    )
    sky_condition_level = let_user_choose_option("sky condition level",
                                                 sky_condition_levels, idx)

    idx, wind_level = get_weather_level(text, wind_levels)
    wind_level = let_user_choose_option("wind level", wind_levels, idx)

    bird_records = []

    extracted_numbers = get_numbers_from_text(text)
    default_observation_characteristic = get_default_observation_characteristic(
        month, day)

    i = 0
    while True:
        selected_species = let_user_search_for_species(species_list, text)
        if selected_species is None:
            break

        number = let_user_enter_number(
            default=1 if i >= len(extracted_numbers) else extracted_numbers[i])

        default_code = default_observation_characteristic["code"]
        observation_characteristic = let_user_search_for_option(
            "observation characteristic",
            observation_characteristics, default_code, show_all=True)

        note = let_user_enter_note()

        land_structure_type_code = let_user_search_for_land_structure(
            land_structures_list)

        bird_records.append({
            "number": number,
            "characteristic": observation_characteristic,
            "method": get_default_observation_method(text),
            "species": selected_species,
            "note": note,
            "land_structure_type": land_structure_type_code
        })

        i += 1

    temp = get_temperature(
        temperature_api_key,
        year,
        month,
        day,
        hour,
        minute,
        duration,
        lat,
        lon,
        mock=args.mock)
    idx, temp_level = get_temperature_level(temp, temperature_levels)
    temp_level = let_user_choose_option(
        f"temperature level (records show t={temp}°C)", temperature_levels, idx)

    return {
        "text": text,
        "geo_str": geo_str,
        "year": year,
        "day": day,
        "month": month,
        "hour": hour,
        "minute": minute,
        "hour_to": hour_to,
        "minute_to": minute_to,
        "sky_condition_level": sky_condition_level,
        "wind_level": wind_level,
        "temperature_level": temp_level,
        "bird_records": bird_records,
    }


def main(args):
    year = 2022
    secrets = get_secrets()
    api_key = secrets["openweathermap_api_key"]

    species = bird_species.get_species()
    species = bird_species.add_freq_rank(species)
    land_structures_df = pd.read_csv("land_structure.csv", sep=";", dtype={"code": int})

    results = []
    data_raw = get_raw_data(args.input_file)
    for data_obj in data_raw:
        try:
            result = create_result_from_raw_data(
                data_obj,
                year=year,
                species_list=species,
                land_structures_list=land_structures_df,
                temperature_api_key=api_key)
        except Exception as e:
            print(f"Processing raw observation data for this record failed with the following exception: {e}")
            result = None

        if result is not None:
            results.append(result)

    with open(args.output_file, "w", encoding="utf8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    args = get_args()
    main(args)
