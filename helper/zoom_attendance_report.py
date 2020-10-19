"""
TODO

Need to figure out some logic around parsing groupings of students, regardless
of the meeting topic. Consider health teachers' use case: they have one zoom
meet for a whole grade level, but only meet with certain students at a time.
They want to know what the attendance rate was for Mrs. Geltzeiler's homeroom;
they don't care about grouping scholars by meet topic like I do.

The best thing to do will probably be to look at the actual group of students
that is a part of any given meeting. Then, check the size of the union between
this meeting, and the other meetings that have been recorded so far. If there
is a large union, we can presume that this meeting is another instance of the
group from before.
"""

import csv
from datetime import datetime
from pathlib import Path
import logging
import string
import re

from fuzzywuzzy import process
from openpyxl import Workbook
from openpyxl.styles import PatternFill

from .csv_parser import BaseCsvParser
try:
    from .manual_zoom_matches import MANUAL_FIXES
except ImportError:
    def MANUAL_FIXES(name):
        """
        For students with silly names the algorithm cannot recognize, write
        this function in the file above, to make individual corrections.
        ./manual_zoom_matches is in the .gitignore because it will likely
        contain student names.
        """
        return name
from .helper import Helper

helper = Helper.read_cache()


class Meeting:
    def __init__(self, path: Path):
        self.path = Path


class ZoomAttendanceReport(BaseCsvParser):
    """
    Parses a directory full of zoom attendance reports and creates a
    longitudinal master report, which shows which students attend over time
    in a recurring meeitng.
    """

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        # Variables initialized in self.open_report()
        self.rows = None
        self.topic = None
        self.datetime = None
        self.path = None
        self.grade_level = None
        self.meetings = set()

    def iter_csvs(self):
        """
        Skip anything that isn't a real csv file. Calls self.open_report(),
        which loads the report into memory as attributes of self; there is no
        need to yield anything, but it yields the path to the current csv
        for convenience.
        """
        for i in self.csv_dir.iterdir():
            if i.name[-4:] != '.csv':
                continue
            if i.name[0] == "~" or i.name[0] == ".":
                continue
            self.open_report(i)
            yield i

    def rename_csv_files(self):
        """
        Provide verbose names to csv file. 
        """
        for report_path in self.iter_csvs():
            if self.rows[2]:
                breakpoint()
                raise Exception(
                    'Zoom report must contain meeting information. The '
                    f'Report at {report_path} does not appear to contain '
                    'meeting information.'
                )
            topic = self.rows[1][1][:9]
            start_time = self.rows[1][2]
            date = start_time.split(' ')[0].replace('/', '-')
            new_name = topic + ' ' + date + '.csv'
            self.path.rename(Path(self.path.parent, new_name))

    def generate_report(self, destination: Path, thresholds=None):
        """
        Coloring:
            Attendance
        Master Sheet:
            The master sheet contains a summary of all data in one place.
            As always
        """
        if not thresholds:
            thresholds = {}
                        # ATTENDANCE COLORING CONSTANTS
        # student's cell will have the following color if they attended for
        # LESS THAN n minutes.
        (
            RED_TIME,
            YELLOW_TIME 
        ) = (
            thresholds.get('red') if thresholds.get('red') else 0,
            thresholds.get('yellow') if thresholds.get('yellow') else 20
        )
        # init student objects to recieve meeting information
        for st in helper.students.values():
            st.meetings = {}
        # gather data into memory
        for _ in self.iter_csvs():
            for row in self.rows[4:]:
                # make student objects self-aware of their attendance record
                if not (student := self.match_student(row[0])):
                    continue
                duration = int(row[2]) if row[2].isdigit() else 0
                student.meetings.setdefault(self.path.stem, duration)
        # init workbook
        OUT = Workbook()
        OUT.remove(OUT.active)
        master_sheet = OUT.create_sheet(title="Master Sheet")
        breakpoint()

    def match_student(self, name):
        """
        Wrapper method that ties together the helper class's find_student
        method, the try_matching_student... method in this class, and some
        custom matches for students with really weird zoom names. Here is also
        where the student's raw zoom name is sanitized (punctuation removed).
        """
        # reference manual fixes, an optional import
        name = MANUAL_FIXES(name)

        # Rough cleaning
        # some use dot to delimit first / last name
        name.replace('.', ' ')
        # remove punctuation
        for char in string.punctuation:
            name.replace(char, '')
        # popular emoticon character
        name.replace('ω', '')
        try:
            return helper.find_nearest_match(name, auto_yes=True)
        except Warning:
            pass
        st = self.try_matching_student_within_grade(name)
        if st:
            return st
        for part in [i for i in re.split(' |.', name) if i]:
            breakpoint()
            st = self.try_matching_student_within_grade(part)
            if st:
                return st

    def try_matching_student_within_grade(self, student_name):
        """
        Unlike in the helper student matching function, this class is aware of
        the grade level of the student it is trying to match. If the helper
        method returns None, this fallback method tries to identify the
        student through process of elimination within their own grade. This
        helps match more students who only provide their first name.
        """
        first_name_match = process.extract(
            student_name,
            [
                s.first_name for s in helper.students.values()
                if s.grade_level == self.grade_level
            ],
            limit=3
        )
        if first_name_match[0][1] > 90:
            # we have a potential match! Let's see if it's truly a match
            # first, re-extract the student object from all students...

            # If the best two matches are the same name, there are two or more
            # students in the grade level with that name. It is therefore
            # impossible to perform a perfect match against only the first name
            if first_name_match[1][0] == first_name_match[0][0]:
                logging.debug(
                    f'Cannot proceed with {student_name}. More than one '
                    f'student in the {self.grade_level}th grade has the first '
                    f'name {first_name_match[0][0]}.'
                )
                return

            # If the first two matches are not the same, that means the first
            # name is unique, and we can make a match within the grade level.
            for n, s in helper.students.items():
                if n.split(' ')[0] == first_name_match[0][0]:
                    logging.debug(
                        'Successful grade level match for '
                        + helper.students[n].name
                    )
                    return helper.students[n]

    def open_report(self, report: Path):
        """
        Opens, reads, and parses zoom report such that IO will not need to
        be performed again.

        assigns attributes:
        self.rows
        self.topic
        self.grade_level
        self.datetime
        self.path
        """
        self.path = report
        self.meetings.update(self.path.stem)
        try:
            self.grade_level = int(report.name[0])
        except ValueError:
            raise NotImplementedError(
                'Grade level is not the first character of the report name.'
            )
        with open(self.path, 'r') as csvfile:
            self.rows = [r for r in csv.reader(csvfile)]
        self.topic = self.rows[1][1][:9]
        time_str = self.rows[1][2]
        (
            month,
            day,
            year,
            hour,
            minute,
            *rest
        ) = [int(i) for i in re.split(r'/| |:', time_str) if i.isdigit()]
        if 'pm' in time_str.lower():
            hour += 12
        self.datetime = datetime(year, month, day, hour, minute)
