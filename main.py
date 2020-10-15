import os
from pathlib import Path
from helper.ClassroomAutomator import FeedbackAutomator
from helper import Helper


if __name__ == 'this':
    atm = FeedbackAutomator(
        os.getenv('EMAIL_USERNAME'),
        os.getenv('EMAIL_PASSWORD_RAW'),
        'Getting Started with Written Music',
        (
            'DeVries_Music_5_Curtis_Institute_of_Music',
            'DeVries_Music_4_Curtis_Institute_of_Music',
        ),
        only_turned_in=True
    )
    for driver, context in atm:
        for a in context.attachments:
            print(a['name'])

if __name__ == '__main__':
    helper = Helper.new_school_year(Path('student.csv'), Path(
        'parent.csv'))
    helper.write_cache()
