#!/bin/bash
rm -f museums.db
sqlite3 about.db ""
yaml-to-sqlite browse.db museums museums.yaml --pk=id
