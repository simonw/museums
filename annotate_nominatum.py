import sqlite_utils
import time
import requests
import tqdm
import json

API_URL = "https://nominatim.openstreetmap.org/reverse?format=jsonv2&extratags=1&namedetails=1&lat={}&lon={}"


def annotate(db):
    for row in tqdm.tqdm(list(db["museums"].rows)):
        data = requests.get(API_URL.format(row["latitude"], row["longitude"])).json()
        update = {"osm_{}".format(key): value for key, value in data["address"].items()}
        update["extratags"] = json.dumps(data["extratags"])
        update["namedetails"] = json.dumps(data["namedetails"])
        db["museums"].update(row["id"], update, alter=True)
        time.sleep(1)


if __name__ == "__main__":
    import sys

    db = sqlite_utils.Database(sys.argv[-1])
    annotate(db)
