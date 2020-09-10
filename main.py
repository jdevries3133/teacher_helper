import os
from pathlib import Path
from helper import Helper
from helper.ClassroomAutomator import FeedbackAutomator

# helper = Helper.new_school_year(Path('basic_info_secret.csv'), Path('contact_info_secret.csv'))
# helper.write_cache()
helper = Helper.read_cache()

atm = FeedbackAutomator(
    os.getenv('GMAIL_USERNAME'),
    os.getenv('GMAIL_PASSWORD_RAW'),
    'Wednesday 9/9 Attendance Question',
    (
        'Geltzeiler_HR_4B',
    ),
)