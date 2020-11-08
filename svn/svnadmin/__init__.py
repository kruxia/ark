import os
from pathlib import Path

PATH = Path(os.path.abspath(__file__)).parent
PACKAGE_PATH = PATH.parent

ARCHIVE_FILES = os.getenv('ARCHIVE_FILES')
DATABASE_URL = os.getenv('DATABASE_URL')
