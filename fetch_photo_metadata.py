import json
import pathlib
import requests
import tqdm
import yaml


def fetch_image_metadata(museums):
    root = pathlib.Path("photos-metadata")
    if not root.exists():
        root.mkdir()
    to_fetch = []
    for museum in museums:
        photo_urls = []
        if museum.get("photo_url"):
            photo_urls.append(museum["photo_url"])
        photo_urls.extend(p["url"] for p in museum.get("photos") or [])
        for photo_url in photo_urls:
            filename = photo_url.split("/")[-1] + ".json"
            output = root / filename
            if not output.exists():
                to_fetch.append((filename, photo_url))
    # Loop through with progress bar
    for filename, url in tqdm.tqdm(to_fetch):
        json_url = url + "?fm=json"
        data = requests.get(json_url).json()
        with open(root / filename, "w") as fp:
            json.dump(data, fp, indent=2)


if __name__ == "__main__":
    with open("museums.yaml") as fp:
        museums = yaml.safe_load(fp)
    fetch_image_metadata(museums)
