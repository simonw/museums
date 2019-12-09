#!/bin/bash
rm -f browse.db
sqlite3 about.db ""
yaml-to-sqlite browse.db museums museums.yaml --pk=id
python annotate_nominatum.py browse.db
python annotate_timestamps.py
sqlite-utils add-column browse.db museums country
sqlite3 browse.db < set-country.sql
sqlite-utils enable-fts browse.db museums name description country osm_city
