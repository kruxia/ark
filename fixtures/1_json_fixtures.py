#!/usr/bin/env python
"""
Use psql to load the mime.types fixture
"""

import json
import os
import subprocess
from glob import glob
from pathlib import Path

DATABASE_URL = os.environ["DATABASE_URL"]
PACKAGE_PATH = Path(__name__).absolute().parent

# load and parse the json fixtures
filepaths = [
    Path(fp) for fp in glob(str(PACKAGE_PATH / "fixtures" / "data" / "*.json"))
]

for filepath in filepaths:
    tablename = filepath.stem.split("-")[-1]
    print("  Load JSON:", filepath.relative_to(PACKAGE_PATH))
    with open(filepath) as f:
        data = json.load(f)
    keys = "(" + ",".join(list(data[0].keys())) + ")"
    values = [
        "("
        + ",".join([f"{val!r}" if val is not None else "null" for val in item.values()])
        + ")"
        for item in data
    ]
    subprocess.check_call(
        [
            "psql",
            DATABASE_URL,
            "-q",
            "-c",
            f"INSERT INTO {tablename} {keys} VALUES {','.join(values)} "
            + "ON CONFLICT DO NOTHING",
        ]
    )
