import os

from .helper import Helper
from .email_ import Email

REQUIRED_VARS = [
    "EMAIL_USERNAME",
    "EMAIL_PASSWORD",
]

for var in REQUIRED_VARS:
    if not os.getenv(var):
        print(
            f"Environment variable {var} is missing, which is necessary for "
            "certain functions within this module."
        )
