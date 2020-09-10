#!/Users/JohnDeVries/repos/teacher_helper/venv/bin/python3.7
import code
import os
import sys
from pprint import pprint
from helper import Helper


def check_cache():
    if Helper.cache_exists():
        return Helper.read_cache()
    else:
        print('Error: Database does not exist.\nHelper object must be cached to use the shell')
        sys.exit()

if '-h' in sys.argv or 'help' in sys.argv:
    print("""
    Supported commands:

    student [name] (-v)
        Pretty prints the dictionary of the matching student. If verbose, also
        print the dict of the students' guardians.

    clock
        Automatically clocks in or out of Paychex, depending on time of day
        and previous clock state.

    [no arguments]
        Run this script with no arguments, and it will enter the shell mode.
        Here, the helper object is instantiated in the local namespace with
        the variable name "helper". All attributes and methods are accessible.
    """)

args = sys.argv + [(''*10)]  # avoid index errors

# student search
if args[1] == 'student':
    helper = check_cache()
    query_name = ' '.join(args[2:])
    try:
        st = helper.find_nearest_match([query_name])[0]
        pprint(st.__dict__)
        if '-v' in args:
            for gu in st.guardians:
                print('\n--\n')
                pprint(gu.__dict__)
        sys.exit()
    except IndexError:
        print(f'Student {args[2]} was not found.')
        sys.exit()

# auto clock in / out
if args[1] == 'clock':
    from helper.paychex import Paychex
    u = os.getenv('PAYCHEX_USR'),  # username
    p = os.getenv('PAYCHEX_PASS')  # password
    with Paychex(u, p) as pcx:
        pcx.clock()
    sys.exit()

helper = check_cache()
code.interact(local=locals())
