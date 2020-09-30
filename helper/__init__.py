import os
from pathlib import Path

from .helper import Helper
from .student import Student


REQUIRED_VARS = [
    'EMAIL_USERNAME',
    'EMAIL_PASSWORD',
]

for var in REQUIRED_VARS:
    if not os.getenv(var):
        raise Warning(
            f'Environment variable {var} is missing, which is necessary for '
            'certain functions within this module.'
        )
