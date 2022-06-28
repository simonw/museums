#!/bin/bash
yaml-to-sqlite browse.db museums museums.yaml --pk=id
python annotate_nominatum.py browse.db
python annotate_timestamps.py
# Ignore errors in following block until set -e:
set +e
sqlite-utils add-column browse.db museums country 2>/dev/null
sqlite3 browse.db < set-country.sql
sqlite-utils disable-fts browse.db museums 2>/dev/null
sqlite-utils enable-fts browse.db museums \
  name description country osm_city \
  --tokenize porter --create-triggers 2>/dev/null
set -e
