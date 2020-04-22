#!/bin/bash
datasette browse.db about.db map.db -p 8211 \
    --reload \
    --template-dir=templates/ \
    --plugins-dir=plugins/ \
    --static css:static/ \
    -m metadata.yaml
