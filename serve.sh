#!/bin/bash
datasette browse.db -p 8211 \
    --reload \
    --template-dir=templates/ \
    --plugins-dir=plugins/ \
    --static css:static/ \
    -m metadata.yaml
