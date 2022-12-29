from pyquery import PyQuery as pq
import requests
import re
# import os.path
# from pathlib import Path
from tqdm import tqdm
import json
# import argparse

from aves_data import genera

aves_bird_list_file = "aves_birds"


def download_species_list_from_aves():
    for language in ["latin", "slovak"]:
        data = dict()
        pbar = tqdm(genera[language], desc=f"{language} genera")
        for genus in pbar:
            pbar.set_description(f"{language} genera: {genus}")

            url = f"http://aves.vtaky.sk/sk/zoology/ajaxLkpzoospecies/action?q={genus}"
            x = requests.get(url)
            if x.status_code == 200:
                results = x.json()
                if not (
                    len(results) == 1
                    and list(results.values())[0] == "ERROR: unknown species!"
                ):
                    data.update(results)

        with open(f"{aves_bird_list_file}_{language}.json", "w") as f:
            json.dump(data, f)


def _load_species_lists_from_files():
    bird_lists = []
    for language in ["latin", "slovak"]:
        with open(f"{aves_bird_list_file}_{language}.json", "r") as f:
            bird_list = json.load(f)
            bird_lists.append(bird_list)
    return bird_lists


def _get_species_record_stats():
    d = pq(filename="species_records.html")
    stats = {}
    for row in d("tr").items():
        species_id, n_records = None, None
        for i, td in enumerate(row.find("td").items()):
            if i == 1:
                species_id = td.find("a").attr("href").split("/")[-1]
            if i == 2:
                n_records = int(td.text())
        if None not in [species_id, n_records]:
            stats[species_id] = n_records
    return stats


def remove_citation_from_scientific_name(name):
    # most obvious case: citation in parentheses, e.g. Anser albifrons (Scopoli, 1789)
    match = re.match(r"(.*)\s+\(.*, [0-9]+\)", name)
    if match:
        return match.group(1)

    # less obvious -- without parentheses, e.g. Anser albifrons Scopoli, 1789
    name_authors = [
        "Linnaeus",
        "Georgi",
        "Brehm",
        "Gray",
        "Latham",
        "Wolf",
        "Tengmalm",
        "Pallas",
        "Pontoppidan",
        "Temminck",
        "Blyth",
        "Buturlin",
        "Baillon",
        "Swinhoe",
        "Vieillot",
        "Nordmann",
        "Gmelin",
        "Michahellis",
        "Tunstall",
        "Montagu",
        "Savigny",
        "Scopoli",
        "Fleischer",
        "Ord",
        "Gunnerus",
        "Borkhausen",
        "Savi",
        "Billberg",
        "Bruch"]
    match = re.match(r"(.*)\s*(" + "|".join(name_authors) + ").*", name)
    if match:
        return match.group(1)

    return name


def get_species():
    species_lat, species_sk = _load_species_lists_from_files()
    species_record_stats = _get_species_record_stats()
    species_ids = set(list(species_lat.keys()) + list(species_sk.keys()))

    species = []
    for species_id in species_ids:
        species.append({
            "name_sk": species_sk.get(species_id),
            "name_lat": species_lat.get(species_id),
            "species_id": species_id,
            "n_records": species_record_stats.get(species_id, 0)
        })
    return sorted(species, key=lambda spec: spec["n_records"], reverse=True)


def main():
    # download_species_list_from_aves()
    print(get_species())


if __name__ == '__main__':
    main()
