import os
from pathlib import Path

from helper import Helper


MODULE_BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
helper = Helper.new_school_year(Path(MODULE_BASE_DIR.parents[0], 'source_data'))

