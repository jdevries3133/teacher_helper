import os
from random import uniform
from time import sleep
from pathlib import Path
from helper import Helper
from helper.ClassroomAutomator import FeedbackAutomator

# helper = Helper.new_school_year(Path('basic_info_secret.csv'), Path('contact_info_secret.csv'))
# helper.write_cache()
if __name__ == 'automator':
    helper = Helper.read_cache()

    class MyAutomator(FeedbackAutomator):
        def assess(self):
            pass

    atm = MyAutomator(
        os.getenv('GMAIL_USERNAME'),
        os.getenv('GMAIL_PASSWORD_RAW'),
        'Wednesday 9/9 Attendance Question',
        (
            'Geltzeiler_HR_4B',
        ),
    )
    atm.loop()
    atm.driver.close()

def main():
    LOGIN= (892,487)
    import pyautogui as pg
    pages = []
    for num in range(5):
        pg.hotkey('command', 'tab')
        current_pages = []
        for i in range(10):
            pg.click(x=1362, y=870)
            sleep(uniform(3, 5))
            im = pg.screenshot()
            im = im.crop((1026, 379, 1852, 1568))
            im = im.convert('RGB')
            current_pages.append(im)
        current_pages[0].save(f'out{num}.pdf', save_all=True, append_images=pages[1:])
        pages += current_pages
        input('Press enter to continue')
        pg.hotkey('command', 'tab')
        sleep(1)
    pages[0].save('master.pdf', save_all=True, append_images=pages[1:])

if __name__ == '__main__':
    main()
