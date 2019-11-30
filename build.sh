#!/bin/bash
rm -f museums.db
sqlite3 about.db ""
yaml-to-sqlite browse.db museums museums.yaml --pk=id
python annotate_nominatum.py browse.db
python annotate_timestamps.py
sqlite-utils enable-fts browse.db museums name description osm_city osm_country
