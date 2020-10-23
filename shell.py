#!/Users/JohnDeVries/repos/teacher_helper/venv/bin/python3.8
import code
import os
from time import sleep
import sys
import webbrowser
import subprocess
from pathlib import Path

from fuzzywuzzy import process

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
        verbose = '-v' in self.args
        if len(self.args) < 2:
            helper = self.check_cache()
            code.interact(local={'helper': helper})
            sys.exit()
        if self.args[1] == 'student':
            try:
                st = self.student_search(
                    ' '.join([i for i in self.args[2:] if i != '-v']),
                    verbose=verbose
                )
                print(st)
                sys.exit()
            except IndexError:
                self.improper_usage()
        elif self.args[1] == 'clock':
            self.clock()
            sleep(1)
        # silly timer
        elif self.args[1] == 'timer':
            self.silly_timer()
        # quick open google classrooms by tag name
        elif self.args[1] == 'gc':
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
        # search for student by parent
        elif self.args[1] == 'parent':
            try:
                match = self.search_by_parent(
                    ' '.join([a for a in self.args[2:] if a != '-v'])
                )
                if match:
                    print(match)
            except IndexError:
                self.improper_usage()
        elif self.args[1] == 'report':
            try:
                st = self.check_cache().find_nearest_match(
                    ' '.join([i for i in self.args[2:] if i != '-v']),
                    auto_yes=True,
                    threshold=60
                )
                print('-' * 30 + 'Contact' + '-' * 30)
                print(st)
                print('-' * 30 + 'Zoom Attendance' + '-' * 30)
                zoom_reports_dir = Path(
                    Path(__file__).parent, 'data', 'zoom_attendance_reports/'
                )
                out = subprocess.call(
                    [
                        'grep',
                        '-nir',
                        st.first_name.lower(),
                        zoom_reports_dir.resolve()
                    ]
                )
            except IndexError:
                self.improper_usage()
        else:
            self.improper_usage()

    def search_by_parent(self, name):
        helper = self.check_cache()

        # create dict of guardians & primary_contacts
        all_guardians = {}
        primary_contacts = {}
        for st in helper.students.values():
            try:
                primary = st.primary_contact
                primary_contacts.setdefault(primary.name, primary)
            except AttributeError:
                pass
            for g in st.guardians:
                all_guardians.setdefault(g.name, g)

        # search for good match (confidence > 85) amongst primary contacts
        primary_match = process.extractOne(
            name,
            [g.name for g in primary_contacts.values()]
        )
        if primary_match[1] > 85:
            return primary_contacts.get(primary_match[0]).student

        # search all parents and guardians if there is no good match in primary
        # contacts
        name_match = process.extractOne(
            name,
            [g.name for g in all_guardians.values()]
        )
        return all_guardians.get(name_match[0]).student

    def student_search(self, name, verbose=False):
        'Search for student, print basic student info.'
        return self.check_cache().find_nearest_match(
            name,
            auto_yes=True,
            threshold=60
        )

    def silly_timer(self):
        try:
            msg = ' '.join(self.args[3:])
            if not msg:
                msg = input(
                    'Enter a message to be spoken after the timer is finished\n'
                )
            Helper().timer(int(self.args[2]), msg)
        except (IndexError, TypeError):
            self.improper_usage()

    @ staticmethod
    def clock(u=None, p=None):
        if not u:
            u = os.getenv('PAYCHEX_USR')  # username
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

        student [name]
            Prints the student according to Student.__str__(). Provides basic
            student and guardian information.

        parent [parent/guardian name]
            Prints the student just like in student search, but search by
            parent instead of by student. Search algorithm prioritizes primary
            contacts; so a fuzzy string match with a primary contact at a
            lower confidence will be returned over a better match against a
            secondary contact.

        report [student name]
            Print a report for the student that includes zoom attendance
            record.

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
