import sqlite_utils
import time
import requests
import tqdm
import json

API_URL = "https://nominatim.openstreetmap.org/reverse?format=jsonv2&extratags=1&namedetails=1&lat={}&lon={}"


def annotate(db):
    if "needs_geocoding" not in db["museums"].columns_dict:
        db["museums"].add_column("needs_geocoding", bool, not_null_default=1)
    for row in tqdm.tqdm(list(db["museums"].rows_where("needs_geocoding = 1"))):
        data = requests.get(API_URL.format(row["latitude"], row["longitude"])).json()
        update = {"osm_{}".format(key): value for key, value in data["address"].items()}
        update["extratags"] = json.dumps(data["extratags"])
        update["namedetails"] = json.dumps(data["namedetails"])
        update["needs_geocoding"] = False
        db["museums"].update(row["id"], update, alter=True)
        time.sleep(1)


if __name__ == "__main__":
    import sys

    db = sqlite_utils.Database(sys.argv[-1])
    annotate(db)
