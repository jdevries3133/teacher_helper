#!/Users/JohnDeVries/repos/teacher_helper/venv/bin/python3.7
import code
import sys
from pprint import pprint
from sparta_helper import Helper

if '-h' in sys.argv or 'help' in sys.argv:
    print("""
    Supported commands:

    student [name]
        puts the nearest match into locals() with the variable name "st"). No
        need to wrap the student name in a string, just pass the name as
        command line arguments. Helper will look for the nearest match and you
        two can work together on it :)
    """)

args = sys.argv + [(''*10)]  # avoid index errors
if Helper.cache_exists():
    helper = Helper.read_cache()
else:
    print('Error: Database does not exist.\nHelper object must be cached to use the shell')
    sys.exit()
if args[1] == 'student':
    query_name = ' '.join(args[2:])
    try:
        st = helper.find_nearest_match([query_name])[0]
        pprint(st.__dict__)
        sys.exit()
    except IndexError:
        print(f'Student {args[2]} was not found.')
        sys.exit()

code.interact(local=locals())
