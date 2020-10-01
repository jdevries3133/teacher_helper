#!/Users/JohnDeVries/repos/teacher_helper/venv/bin/python3.8
import code
import os
import sys
import webbrowser
from helper import Helper
from helper.paychex import Paychex


class ShellUtils:

    def __init__(self, args):
        self.args = args

    def route(self):
        'Route self.args to various utilities'
        if '-h' in self.args or 'help' in self.args:
            self.print_help()
            sys.exit()
        if '-v' in self.args:
            verbose = True
        else:
            verbose = False
        if len(self.args) < 2:
            helper = self.check_cache()
            code.interact(local={'helper': helper})
        if self.args[1] == 'student':
            try:
                self.student_search(
                    ' '.join([i for i in self.args[2:] if i != '-v']),
                    verbose=verbose
                )
            except IndexError:
                self.improper_usage()
        elif self.args[1] == 'clock':
            self.clock()
        # silly timer
        if self.args[1] == 'timer':
            try:
                msg = ' '.join(self.args[3:])
                if not msg:
                    msg = input(
                        'Enter a message to be spoken after the timer is finished\n'
                    )
                Helper().timer(int(self.args[2]), msg)
            except (IndexError, TypeError):
                self.improper_usage()
        # quick open google classrooms by tag name
        if self.args[1] == 'gc':
            valid_tags = {
                '6': 'https://classroom.google.com/u/0/c/MTU4NTE3OTg5MDc0',
                '5': 'https://classroom.google.com/u/0/c/MTU4NTE3OTg5MDMz',
                '4': 'https://classroom.google.com/u/0/c/MTU4NDc3MDE2ODA0',
                'g': 'https://classroom.google.com/u/0/c/MTUyNDYzMzI3MjQx',
            }
            try:
                webbrowser.open(valid_tags[self.args[2]])
            except KeyError:
                print(
                    'Invalid google classroom tag name. Acceptable tags are:\n'
                    + '\t'.join(valid_tags.keys())
                )

    def student_search(self, name, verbose=False):
        'Search for student, print basic student info.'
        try:
            st = self.check_cache().find_nearest_match(name)
            print(st.__str__(verbose))
            sys.exit()
        except IndexError:
            print(f'Student {sys.argv[2]} was not found.')
            sys.exit()

    @ staticmethod
    def clock(u=None, p=None):
        if not u:
            u = os.getenv('PAYCHEX_USR'),  # username
        if not p:
            p = os.getenv('PAYCHEX_PASS')  # password
        with Paychex(u, p) as pcx:
            if 'in' in sys.argv:
                pcx.clock_in()
            elif 'out' in sys.argv:
                pcx.clock_out()
            else:
                pcx.clock()
        sys.exit()

    def improper_usage(self):
        self.print_help()
        print('IMPROPER USAGE, SEE HELP ABOVE')
        sys.exit()

    @ staticmethod
    def check_cache():
        if Helper.cache_exists():
            return Helper.read_cache()
        print(
            'Error: Database does not exist.\nHelper object must be cached '
            'to use the shell'
        )
        sys.exit()

    @ staticmethod
    def print_help():
        print("""
        Supported commands:

        student [name] (-v)
            Pretty prints the dictionary of the matching student. If verbose,
            also print the dict of the students' guardians.

        clock
            Automatically clocks in or out of Paychex, depending on time of day
            and previous clock state.

        timer [minutes] [message]
            Start a timer that will say [message] after [minutes]. The message
            will be spoken by a robot voice.

        [no arguments]
            Run this script with no arguments, and it will enter the shell mode.
            Here, the helper object is instantiated in the local namespace with
            the variable name "helper". All attributes and methods are accessible.
        """)


if __name__ == '__main__':
    ShellUtils(sys.argv).route()
