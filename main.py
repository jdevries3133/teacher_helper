import os
from random import uniform
from time import sleep
from pathlib import Path
import pyautogui as pg
from helper import Helper
from helper.ClassroomAutomator import FeedbackAutomator

pg.PAUSE = 1

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

def is_booted(im):
    px = im.getpixel((54, 404))
    if px == (44, 117, 70):
        return True
    return False


def capture():
    sleep(uniform(3, 5))
    im = pg.screenshot()
    im = im.crop((1026, 379, 1852, 1568))
    im = im.convert('RGB')
    return im


def login_again(page):
    pg.hotkey('command', 'w')
    pg.click(705, 351)
    sleep(2)
    pg.click(908, 485)
    pg.hotkey('command', 'tab')
    input(f'Navigate to page {page}, then press enter to continue')
    sleep(8)
    pg.hotkey('command', 'tab')
    sleep(1)


def main():
    pages = []
    pg.hotkey('command', 'tab')
    for i in range(100):
        im = capture()
        if is_booted(im):
            login_again(i)
            im = capture()
        pages.append(im)
        pg.click(1358, 870)
    pages[0].save('master.pdf', save_all=True, append_images=pages[1:])

if __name__ == '__main__':
    main()
