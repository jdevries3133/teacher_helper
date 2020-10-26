import os
import logging
from pathlib import Path

from .helper import Helper
from .student import Student
from .zoom_attendance_report import MeetingSet, ExcelWriter


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

logging.basicConfig(
    format="FILE %(filename)s:FUNC %(funcName)s:LINE %(lineno)s:%(levelname)s:%(message)s",
    filename="helper.log",
    level=logging.DEBUG
)
