import json
import pathlib
import sqlite_utils


def load_image_metadata():
    root = pathlib.Path("photos-metadata")
    to_insert = []
    for path in root.glob("*.json"):
        with open(path) as fp:
            data = json.load(fp)
            data["filename"] = path.name.replace(".json", "")
            to_insert.append(data)

    db = sqlite_utils.Database("browse.db")
    db["raw_photos"].insert_all(
        to_insert, pk="filename", alter=True, replace=True
    )

    db.create_view("photos", """
        select 'https://niche-museums.imgix.net/' || filename as url,
            PixelWidth as width,
            PixelHeight as height
        from raw_photos
    """, replace=True)

if __name__ == "__main__":
    load_image_metadata()
