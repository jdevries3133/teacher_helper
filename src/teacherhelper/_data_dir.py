"""Interface to ~/.teacherhelper or whatever path the user choose to store
data for this module via the `HELPER_DATA` environment variable."""

import os
from pathlib import Path


# create a Path object representing the DATA_DIR, either a user provided path
# or ~/.teacherhelper
user_specified_data_dir = os.getenv('HELPER_DATA')
if not user_specified_data_dir:
    DATA_DIR = Path(os.path.expanduser('~'), '.teacherhelper')
else:
    DATA_DIR = Path(user_specified_data_dir)
    if not DATA_DIR.exists():
        raise FileNotFoundError(f'path {DATA_DIR} does not exist')


def get_path_inside_data_dir(path):
    return Path(DATA_DIR, path)
