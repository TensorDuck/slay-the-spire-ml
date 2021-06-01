"""Script for extracting all the victorious decks from the official data dump"""
import gzip
import json
import os

from slayer.globals import RESOURCE_LOCATION
from slayer.preprocess import filter_records_by_victory, make_resources, get_cards

if __name__ == "__main__":
    print("starting preprocess_good_decks")

    # dir where the raw data is
    data_dir = "data/full/Monthly_2020_11"
    all_files = os.listdir(data_dir)

    # get records only where there is a victory
    all_victory_runs = []
    for idx, fn in enumerate(all_files):
        with gzip.open(f"{data_dir}/{fn}", "r") as fin:  # 4. gzip
            json_bytes = fin.read()  # 3. bytes (i.e. UTF-8)

        json_str = json_bytes.decode("utf-8")  # 2. string (i.e. JSON)
        data = json.loads(json_str)
        victory_runs = filter_records_by_victory(data)
        all_victory_runs.extend(victory_runs)
        if idx % 10 == 0:
            print(len(victory_runs) / len(data))  # fraction of victories
            print(len(all_victory_runs))  # number of total victors

        # save only the first 10000 for quick testing for now
        if len(all_victory_runs) > 10000:
            break

    with open(f"{RESOURCE_LOCATION}/victory.json", "w") as f:
        json.dump(all_victory_runs, f, indent=4)

    make_resources(all_victory_runs)
