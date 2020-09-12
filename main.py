import os
from pathlib import Path
from helper import Helper
from helper.ClassroomAutomator import FeedbackAutomator


if __name__ == '__main__':
    helper = Helper.read_cache()

    class MyAutomator(FeedbackAutomator):
        def assess(self):
            pass

    atm = MyAutomator(
        os.getenv('GMAIL_USERNAME'),
        os.getenv('GMAIL_PASSWORD_RAW'),
        'Wednesday 9/9 Attendance Question',
        (
            'Geltzeiler_HR_4B\n2020-2021',
        ),
    )
    atm.loop()
    atm.driver.close()