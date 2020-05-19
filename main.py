import os
from pathlib import Path

from sparta_helper import Helper

if __name__ == '__main__':
    helper = Helper.read_cache()

    unres_pths = [
        Path('google_classrooms'),
        Path('flipgrid'),
        Path('edpuzzle'),
    ]

    pths = [Path.absolute(p) for p in unres_pths]
    helper.find_non_participators(pths)
