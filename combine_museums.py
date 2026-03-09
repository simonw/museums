#!/usr/bin/env python3
"""
Combine individual museums/*.yaml files into a single YAML list on stdout.
Used by build.sh to feed yaml-to-sqlite.
"""

import sys
from pathlib import Path

import yaml


def combine_museums(museums_dir="museums"):
    museums = []
    for path in sorted(Path(museums_dir).glob("*.yaml"), key=lambda p: int(p.stem)):
        museums.append(yaml.safe_load(path.read_text()))
    return museums


if __name__ == "__main__":
    museums = combine_museums()
    yaml.dump(museums, sys.stdout, default_flow_style=False, allow_unicode=True, sort_keys=False)
