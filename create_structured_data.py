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

from aves_data import sky_condition_levels, wind_levels, observation_characteristics, observation_methods, temperature_levels, genera

aves_bird_list_file = "aves_birds"
name_sim_threshold = 50


def get_default_observation_method(text):
    for word in ["ozyva", r"vola[^v]", "spieva"]:
        if re.search(word, text):
            return {"name": "AKUSTICKY MONITORING - akustický monitoring", "code": "15"}
    return {"name": "VIZUAL - vizuálne pozorovanie", "code": "8"}

def get_temperature_level(temp):
    for level in temperature_levels:
        if temp < max(level["range"]) and temp >= min(level["range"]):
            return level
    return None

def get_default_observation_characteristic(month):
    if month >= 4 and month < 8:
        return {"name": "A0 - výskyt od 1.4. do 31.7.", "code": "19"}
    else:
        return {"name": "M_MV - migrácia alebo výskyt v mimohniezdnom období", "code": "36"}

def strip_accents(s):
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )


def get_similarity_score(text, targets):
    def _sim_func(text1, text2):
        return fuzz.partial_ratio(text1, text2)

    score = max([_sim_func(text, target) for target in targets])
    return score


def get_weather_level(text, weather_level_data):
    scores = {}

    for i, level_data in enumerate(weather_level_data):
        descriptive_words = level_data["descriptive_words"]
        score = get_similarity_score(text.lower(), descriptive_words)
        scores[i] = score

    top_result_idx = max(scores, key=scores.get)

    return weather_level_data[top_result_idx]


def get_bird_names(text, bird_lists, n):
    candidates = []
    for bird_list in bird_lists:
        candidates_for_language = []
        for bird_name, bird_code in bird_list.items():
            sim1 = fuzz.partial_ratio(
                strip_accents(text).lower(), strip_accents(bird_name).lower()
            )
            first_part_of_name = strip_accents(bird_name).lower().strip().split(" ")[0]
            sim2 = fuzz.partial_ratio(strip_accents(text).lower(), first_part_of_name)
            if sim1 > name_sim_threshold or sim2 > name_sim_threshold:
                candidates_for_language.append((max(sim1, sim2), bird_name, bird_code))
        candidates.extend(candidates_for_language)

    if len(candidates) > 0:
        candidates.sort(key=lambda t: t[0], reverse=True)
    return candidates[:n]


def get_secrets():
    with open("secrets.json") as f:
        return json.load(f)


def get_number_from_text(text):
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


def get_temperature(api_key, year, month, day, hour, minute, duration, lat, lon):
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
    x = requests.get(url)
    if x.status_code == 200:
        return x.json()["data"][0]["temp"]
    return None



def download_bird_list_from_aves():
    for language in ["latin", "slovak"]:
        data = dict()
        for genus in genera[language]:
            url = f"http://aves.vtaky.sk/sk/zoology/ajaxLkpzoospecies/action?q={genus}"
            x = requests.get(url)
            if x.status_code == 200:
                results = x.json()
                results = {v: k for k, v in results.items()}
                if not (
                    len(results) == 1
                    and list(results.keys())[0] == "ERROR: unknown species!"
                ):
                    print(f"{genus}: {results}")
                    data.update(results)

        with open(f"{aves_bird_list_file}_{language}.json", "w") as f:
            json.dump(data, f)


def load_bird_list():
    bird_lists = []
    for language in ["latin", "slovak"]:
        with open(f"{aves_bird_list_file}_{language}.json", "r") as f:
            bird_list = json.load(f)
            bird_lists.append(bird_list)
    return bird_lists


def get_args():
    parser = argparse.ArgumentParser(
        description="Convert GPX waypoint data into JSON data."
    )
    parser.add_argument("-i", "--input_file", type=str, help="The GPX file to process", required=True)
    parser.add_argument("-o", "--output_file", type=str, help="The output JSON file name", required=True)
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


def main(args):
    year = 2022
    secrets = get_secrets()
    api_key = secrets["openweathermap_api_key"]
    
    # download_bird_list_from_aves()
    bird_list_latin, bird_list_slovak = load_bird_list()

    results = []
    data_raw = get_raw_data(args.input_file)
    for data_obj in data_raw:
        text = data_obj["text"]
        lat = data_obj["lat"]
        lon = data_obj["lon"]

        geo_str = f"POINT({lon} {lat})"

        print(f"===== {text} ======")

        dt = get_datetime_from_text(text)
        if dt is None:
            continue
        day, month, hour, minute, duration = dt
        if duration is None:
            duration = timedelta(minutes=2)
        print(day, month, hour, minute, duration)
        dt_to = datetime.datetime(year, month, day, hour=hour, minute=minute) + duration
        hour_to = dt_to.hour
        minute_to = dt_to.minute

        numbers = get_number_from_text(text)
        print(f"numbers of birds: {numbers}")

        sky_condition_level = get_weather_level(
            text, sky_condition_levels
        )
        print(f"sky condition level: {sky_condition_level}")

        wind_level = get_weather_level(text, wind_levels)
        print(f"wind level: {wind_level}")

        top_bird_names = get_bird_names(
            text, [bird_list_slovak, bird_list_latin], n=5 * len(numbers)
        )

        temp = get_temperature(api_key, year, month, day, hour, minute, duration, lat, lon)
        temp_level = get_temperature_level(temp)
        print(f"temperature: {temp:.1f} degrees\n\t{temp_level}")

        bird_records = [{
            "number": n,
            "characteristic": get_default_observation_characteristic(month),
            "method": get_default_observation_method(text),
            "birds": top_bird_names
        } for n in numbers]

        result = {
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
        results.append(result)

    with open(args.output_file, "w") as f:
        json.dump(results, f, indent=4)


if __name__ == "__main__":
    args = get_args()
    main(args)
