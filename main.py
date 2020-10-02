from pathlib import Path
import os
from helper.ClassroomAutomator import FeedbackAutomator
from helper import Helper


if __name__ == '':
    atm = FeedbackAutomator(
        os.getenv('EMAIL_USERNAME'),
        os.getenv('EMAIL_PASSWORD_RAW'),
        'Monday 9/28 Attendance Question',
        (
            'Geltzeiler_HR_4B\n2020-2021',
        ),
    )
    for driver, context in atm.iter_assess():
        breakpoint()

if __name__ == '__main__':
    helper = Helper.new_school_year(Path('student.csv'), Path(
        'guardian.csv'))
    helper.write_cache()
