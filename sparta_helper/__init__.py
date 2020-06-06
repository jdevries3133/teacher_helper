from .helper import Helper
from .student import Student

import os
from pathlib import Path

env_vars = [
    'GENESIS_USERNAME',
    'GENESIS_PASSWORD',
    'GMAIL_USERNAME',
    'GMAIL_PASSWORD', 
 ]

for env_var in env_vars:
    if not os.getenv(env_var):
        raise Warning(
            f'Environment variable {env_var} is missing, which is necessary for certain functions within this module.'
        )