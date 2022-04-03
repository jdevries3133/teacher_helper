"""Interface to ~/.teacherhelper or whatever path the user choose to store
data for this module via the `HELPER_DATA` environment variable."""

import os
from pathlib import Path


def get_data_dir() -> Path:
    # create a Path object representing the DATA_DIR, either a user provided path
    # or ~/.teacherhelper
    user_specified_data_dir = os.getenv("HELPER_DATA")
    if not user_specified_data_dir:
        return Path(os.path.expanduser("~"), ".teacherhelper")
    else:
        data_dir = Path(user_specified_data_dir)
        if not data_dir.exists():
            raise FileNotFoundError(f"path {data_dir} does not exist")

        return data_dir
