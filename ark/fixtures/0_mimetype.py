#!/usr/bin/env python
"""
Use psql to load the mime.types fixture
"""

import os
import subprocess
from pathlib import Path

DATABASE_URL = os.environ["DATABASE_URL"]
PACKAGE_PATH = Path(__name__).absolute().parent

# load and parse the mime.types file
mimetypes_path = PACKAGE_PATH / "fixtures" / "data" / "_mime.types"

with open(mimetypes_path) as f:
    raw_data = f.read()

data = [
    {"name": line[0], "exts": line[1:]}
    for line in [line.split() for line in raw_data.split("\n")]
]
mimetype_values = ",".join([f"('{item['name']}')" for item in data])
subprocess.run(
    [
        "psql",
        DATABASE_URL,
        "-q",
        "-c",
        f"INSERT INTO mimetype (name) VALUES {mimetype_values} "
        + "ON CONFLICT DO NOTHING",
    ]
)
ext_values = ",".join(
    [f"('{item['name']}', '{ext}')" for item in data for ext in item["exts"]]
)
subprocess.run(
    [
        "psql",
        DATABASE_URL,
        "-q",
        "-c",
        f"INSERT INTO ext_mimetype (name, ext) VALUES {ext_values} "
        + "ON CONFLICT DO NOTHING",
    ]
)
