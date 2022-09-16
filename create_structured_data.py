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

aves_bird_list_file = "aves_birds"
name_sim_threshold = 50

sky_condition_levels = [{
    "name": "jasno (obloha úplne bez oblačnosti)",
    "code": 1,
    "descriptive_words": ["jasno"]
},{
    "name": "polojasno (veľká väčšina oblohy bez oblačnosti)",
    "code": 2,
    "descriptive_words": ["polojasno"]
},{
    "name": "polooblačno (asi polovica oblohy je pokrytá oblačnosťou)",
    "code": 3,
    "descriptive_words": ["polooblacno"]
},{
    "name": "oblačno (väčšina oblohy je pokrytá oblačnosťou)",
    "code": 4,
    "descriptive_words": ["oblacno"]
},{
    "name": "zamračené (obloha je úplne pokrytá oblačnosťou)",
    "code": 5,
    "descriptive_words": ["zamracene"]
},{
    "name": "hmla / zamračené nízkou inverznou oblačnosťou (na horách jasno)",
    "code": 6,
    "descriptive_words": ["hmla", "inverzia"]
}]

wind_levels = [
{
    "name": "bezvetrie",
    "code": 1,
    "descriptive_words": ["bezvetrie"]
},{
    "name": "slabý vietor (vietor pohybuje iba listami na stromoch, ale nie konármi)",
    "code": 2,
    "descriptive_words": ["listy", "slaby vietor"]
},{
    "name": "mierny vietor (vietor už pohybuje aj konármi stromov)",
    "code": 3,
    "descriptive_words": ["konare", "mierny vietor"]
},{
    "name": "silný vietor (vietor pohybuje celým stromom, môže dochádzať k odlamovaniu konárov)",
    "code": 4,
    "descriptive_words": ["stromy", "silny vietor"]
},{
    "name": "víchrica (na stromoch sa odlamujú veľké konáre, alebo sa vyvracajú celé stromy)",
    "code": 5,
    "descriptive_words": ["vichrica"]
}]

data_raw = [{
    "text": "rybarik hirundo rustica 2 sedi na trstine pri Ciernej vode 5.8. 12:23 13:23 zamrac bezv",
    "lon": 17.469024641149367,
    "lat": 48.3266521
}]

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

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

    return weather_level_data[top_result_idx]["code"], weather_level_data[top_result_idx]["name"]


def get_bird_names(text, bird_lists, n):
    candidates = []
    for bird_list in bird_lists:
        candidates_for_language = []
        for bird_name, bird_code in bird_list.items():
            sim = fuzz.partial_ratio(strip_accents(text).lower(), strip_accents(bird_name).lower())
            if sim > name_sim_threshold:
                candidates_for_language.append((sim, bird_name, bird_code))
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
        duration = timedelta(hours=int(time_matches[1].split(":")[0])-hour, minutes=int(time_matches[1].split(":")[1])-minute)

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


def get_temperature(api_key, year, month, day, hour, minute, duration):
    # +1h (CET) + 1h (if daylight saving applies)
    hour_adjustment = timedelta(hours=1 + (1 if is_summer_time(year, month, day) else 0))
    print(f"hour_adjustment: {hour_adjustment}")
    
    start_timestamp = (datetime.datetime(year, month, day, hour=hour, minute=minute) - hour_adjustment).timestamp()
    end_timestamp = (datetime.datetime(year, month, day, hour=hour, minute=minute) + duration - hour_adjustment).timestamp()
    
    mid_timestamp = int((start_timestamp + end_timestamp) / 2)
    url = f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&dt={mid_timestamp}&appid={api_key}&units=metric"
    x = requests.get(url)
    return x.json()["data"][0]["temp"]

def is_latin_name(name):
    if "Linné" in name:
        return True
    if re.match(r".*[ľščťžýáíéúäňôďŕóĺ].*", name):
        return False
    if re.match(r".*\(.*, [0-9]{4}.*\)", name):
        return True
    if re.match(r".*([0-9]{3,4}|sp\.).*", name):
        return True
    if re.match(r"^(Acanthis|Acrocephalus|Anas|Anser|Anthus|Asio|Aythya|Certhia|Delichon|Dendrocopos|Falco|Fringilla|Hydrocoloeus|Larus|Linaria|Luscinia|Mergus|Muscicapa|Passer|Phoenicopterus|Phoenicurus|Phylloscopus|Poecile|Regulus|Saxicola|Sylvia).*", name):
        return True
    return False

def download_bird_list_from_aves():
    slovak_letters = ["a", "á", "ä", "b", "c", "č", "d", "ď", "dz", "dž", "e", "é", "f", "g", "h", "ch", "i", "í", "j", "k", "l", "ĺ", "ľ", "m", "n", "ň", "o", "ó", "ô", "p", "q", "r", "ŕ", "s", "š", "t", "ť", "u", "ú", "v", "w", "x", "y", "ý", "z", "ž"]
    all_data = dict()
    for first_letter in slovak_letters:
        for second_letter in slovak_letters:
            url = f"http://aves.vtaky.sk/sk/zoology/ajaxLkpzoospecies/action?q={first_letter}{second_letter}&limit=1000"
            x = requests.get(url)
            results = x.json()
            results = {v: k for k, v in results.items()}
            if not (len(results) == 1 and list(results.keys())[0] == "ERROR: unknown species!"):
                print(f"{first_letter}{second_letter}: {results}")
                all_data.update(results)

    data_by_language = {"slovak": {}, "latin": {}}
    for name, code in all_data.items():
        language = "latin" if is_latin_name(name) else "slovak"
        data_by_language[language][name] = code

    for language in ["latin", "slovak"]:    
        with open(f"{aves_bird_list_file}_{language}.json", "w") as f:
            json.dump(data_by_language[language], f)


def load_bird_list():
    bird_lists = []
    for language in ["latin", "slovak"]:
        with open(f"{aves_bird_list_file}_{language}.json", "r") as f:
            bird_list = json.load(f)
            bird_lists.append(bird_list)
    return bird_lists

def get_args():
    parser = argparse.ArgumentParser(description="Convert GPX waypoint data into JSON data.")
    parser.add_argument("--input_file", type=str, help="The GPX file to process", required=True)
    parser.add_argument("--output_file", type=str, help="The output JSON file name", required=True)
    return parser.parse_args()

def get_raw_data(input_file):
    data = []

    with open(input_file, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        for waypoint in gpx.waypoints:
            data.append({
                "text": waypoint.name,
                "lat": waypoint.latitude,
                "lon": waypoint.longitude
                })
    return data

def main(args):
    year = 2022
    secrets = get_secrets()
    api_key = secrets["openweathermap_api_key"]
    results = []

    data_raw = get_raw_data(args.input_file)
    for data_obj in data_raw:
        text = data_obj["text"]
        lat = data_obj["lat"]
        lon = data_obj["lon"]

        geo_str = f"POINT({lat} {lon})"

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

        sky_condition_level_code, sky_condition_level_name = get_weather_level(text, sky_condition_levels)
        print(f"sky condition level: {sky_condition_level_name}")

        wind_level_code, wind_level_name = get_weather_level(text, wind_levels)
        print(f"wind level: {wind_level_name}")
        

        # download_bird_list_from_aves()

        bird_list_latin, bird_list_slovak = load_bird_list()
        # print(bird_list_slovak)

        top_bird_names = get_bird_names(text, [bird_list_slovak, bird_list_latin], n=5*len(numbers))
        print(top_bird_names)

        # temp = get_temperature(api_key, year, month, day, hour, minute, duration)
        temp = 23.8
        print(f"Temperature: {temp:.1f} degrees")
        
        bird_records = [{"number": n, "birds": top_bird_names} for n in numbers]

        result = {
            "text": text,
            "geo_str": geo_str,
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "minute": minute,
            "hour_to": hour_to,
            "minute_to": minute_to,
            "sky_condition_level": sky_condition_level_code,
            "sky_condition_level_name": sky_condition_level_name,
            "wind_level": wind_level_code,
            "wind_level_name": wind_level_name,
            "temperature": temp,
            "bird_records": bird_records 
        }
        results.append(result)

    with open(args.output_file, "w") as f:
        json.dump(results, f, indent=4)


if __name__ == '__main__':
    args = get_args()
    main(args)
