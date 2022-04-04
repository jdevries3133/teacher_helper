import os

from .helper import Helper  # raises DeprecationWarning on instantiation
from .email_ import Email

RECCOMENDED_ENV = [
    "EMAIL_USERNAME",
    "EMAIL_PASSWORD",
]

for var in RECCOMENDED_ENV:
    if not os.getenv(var):
        print(
            f"Environment variable {var} is missing, which is necessary for "
            "certain functions within this module."
        )
