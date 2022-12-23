import json

if __name__ == "__main__":
    with open("uploader_template.js", "r") as f:
        uploader_template = f.read()

    with open("data_checked.json", "r", encoding="utf8") as f:
        json_data = json.load(f)

    for data in json_data:
        data_to_inject = {}
        if data["bird_records"] is not None:
            data_to_inject["bird_records"] = [{
                "species_id": r["birds"][0][1],
                "name": r["birds"][0][0],
                "count": r["number"],
                "observation_characteristic": r["characteristic"]["code"],
                "observation_method": r["method"]["code"]
            } for r in data["bird_records"]]
        else:
            data_to_inject["bird_records"] = []

        for key in ["geo_str", "day", "month", "year",
                    "hour", "minute", "minute_to", "hour_to", "text"]:
            data_to_inject[key] = data[key]

        for key in ["sky_condition_level", "wind_level", "temperature_level"]:
            data_to_inject[key] = data[key]["code"]

        uploader_code = uploader_template.format(**data_to_inject)
        input("\n\nPress Enter to continue.\n\n")
        print(uploader_code)
