#!/usr/bin/env python3

"""
Access the teacher_helper module functionality through a command line
interface. Invoke directly from within an activated virtual environment,
or use a wrapper script like this one:

    https://github.com/jdevries3133/my_shell_scripts/blob/master/emp
"""

import code
import os
from time import sleep
import sys
import webbrowser
import subprocess
from pathlib import Path

from fuzzywuzzy import process

from teacherHelper import Helper, Email
from paychex import Paychex

# TODO: re-implement implement with argparse (https://docs.python.org/3/library/argparse.html)


class ShellUtils:

    def __init__(self, args):
        self.args = args
        # emp new fix
        if len(self.args) > 1 and self.args[1] == 'new':
            self.helper = Helper()
            return
        self.helper = self.check_cache()  # will print help if cache doesn't exist

    def route(self):
        'Route self.args to various utilities'

        # check for verbose of help
        if '-h' in self.args or '--help' in self.args:
            self.print_help()
            sys.exit()
        verbose = '-v' in self.args

        # launch python shell if there are no arguments
        if len(self.args) < 2:
            code.interact(local={
                'helper': self.helper,
                'Email': Email
            })
            sys.exit()

        # route argument to utility functions

        # COMMAND "emp student" => search for student info
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

        # COMMAND "emp clock" => clock in to paychex (unstable)
        elif self.args[1] == 'clock':
            self.clock()
            sleep(1)

        # COMMAND "emp timer" => start silly timer
        elif self.args[1] == 'timer':
            self.silly_timer()

        # COMMAND "emp gc" => quick open google classrooms by tag name
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

        # COMMAND "emp parent" => search for student by parent
        elif self.args[1] == 'parent':
            try:
                match = self.search_by_parent(
                    ' '.join([a for a in self.args[2:] if a != '-v'])
                )
                if match:
                    print(match)
            except IndexError:
                self.improper_usage()

        # COMMAND "emp new" => refresh cache from files in ./data dir
        elif self.args[1] == 'new':
            new = Helper.new_school_year(
                Path(Path(__file__).parent, 'data', 'students.csv'),
                Path(Path(__file__).parent, 'data', 'parents.csv'),
            )
            new.write_cache()
            print('Cache updated.')
            sys.exit()

        # COMMAND "emp report" => grep for zoom attendance history through
                                  # downloaded reports
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
        elif self.args[1] == 'email':
            self.email()
        else:
            self.improper_usage()

    def email(self):
        """
        THIS ONLY WORKS FOR EMAILING STUDENTS. It uses the lookup function
        to grab their email, which is where the true convenience lies; it
        saves the step of searching for the student email since their emails
        are gibberish.

        """
        # TODO: implement CC'ing

        # assemble student name and message
        data = {'name': '', 'message': '', 'subject': ''}
        appending_to = 'name'
        for word in self.args[1:]:
            if not word:
                continue
            if word == '--message':
                appending_to = 'message'
                continue
            if word == '--subject':
                appending_to = 'subject'
                continue
            data[appending_to] += word + ' '
        data = {k: v.strip() for k, v in data.items()}

        # confirm details
        if not (st := self.confirm_email_data(data)):
            print('Ok, email not sent')
            sys.exit()

        # send email
        with Email() as emlr:
            emlr.send(
                to=st.email,
                subject=data['subject'],
                message=data['message'].split(' ')
            )

    def confirm_email_data(self, data):
        """
        Returns confirmed st (Student object instance) or False
        """
        st = self.helper.find_nearest_match(data.get('name'), auto_yes=True)
        if self._confirm(
            f"Is this who you want to email? {st.name} (y/n): "
        ) and self._confirm(
            f'Is this the correct subject?\n\t\"{data.get("subject")}\"\n(y/n) '
        ) and self._confirm(
            f'Is this the correct message?\n\t\"{data.get("message")}\"\n(y/n) '
        ):
            return st
        return False

    @ staticmethod
    def _confirm(message):
        inp = None
        while not (inp := inp if inp else None):
            inp = input(message)
            if inp.lower() == 'y':
                return True
            if inp.lower() == 'n':
                return False
            print('Please enter "y" or "n"')

    def search_by_parent(self, name):
        self.helper

        # create dict of guardians & primary_contacts
        all_guardians = {}
        primary_contacts = {}
        for st in self.helper.students.values():
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

        new
            Will refresh the cache by loading in spreadsheets at ./data/students.csv
            and ./data/parents.csv.

        [no arguments]
            Run this script with no arguments, and it will enter the shell mode.
            Here, the helper object is instantiated in the local namespace with
            the variable name "helper". All attributes and methods are accessible.
        """)


if __name__ == '__main__':
    ShellUtils(sys.argv).route()
