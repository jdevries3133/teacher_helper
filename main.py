import os
from pathlib import Path

from sparta_helper import Helper

if __name__ == 'ph':
    helper = Helper.read_cache()

    unres_pths = [
        Path('google_classrooms'),
        Path('flipgrid'),
        Path('edpuzzle'),
    ]

    pths = [Path.absolute(p) for p in unres_pths]
    helper.find_non_participators(pths)

if __name__ == '__main__':
    path_in = Path.resolve(Path('.', 'soundtrap_in.csv'))
    path_out = Path.resolve(Path('.', 'soundtrap_out.csv'))
    path_update = Path.resolve(Path('.', 'soundtrap_update.csv'))

    helper = Helper.read_cache()
    helper.soundtrap_update(path_in, path_out, path_update)
    



    