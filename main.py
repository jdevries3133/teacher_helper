from pathlib import Path
from helper import Helper

helper = Helper.new_school_year(Path('basic_info_secret.csv'), Path('contact_info_secret.csv'))

"""
from helper.zoom import Zoom

import pyautogui as pg

pg.hotkey('command', 'tab')
zm = Zoom()
zm.rename_student('test', 'test')
"""
