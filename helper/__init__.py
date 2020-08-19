from .helper import Helper
from .student import Student

import os
from pathlib import Path

REQUIRED_VARS = [
    'GENESIS_USERNAME',
    'GENESIS_PASSWORD',
    'GMAIL_USERNAME',
    'GMAIL_PASSWORD', 
 ]

for var in REQUIRED_VARS:
    if not os.getenv(var):
        raise Warning(
            f'Environment variable {env_var} is missing, which is necessary for '
            'certain functions within this module.'
        )