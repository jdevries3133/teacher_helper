from copy import copy
from datetime import datetime
import logging
import string
import re

from fuzzywuzzy import process
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font

try:
    from .manual_zoom_matches import MANUAL_FIXES
except ImportError:
    def MANUAL_FIXES(name):
        """
        For students with silly names the algorithm cannot recognize, write
        this function in the file above to make individual corrections.
        ./manual_zoom_matches.py is in the .gitignore because it will
        contain student names.
        """
        return name


from .helper import Helper

logger = logging.getLogger(__name__)


class HelperConsumer:
    helper = Helper.read_cache()


class Meeting(HelperConsumer):
    """
    Single zoom meeting. Opens and reads a CSV file, as downloaded from
    zoom.

    Attrs:
        - rows
        - topic
        - datetime

    """

    def __init__(self, csv_string: str):
        super().__init__()
        self.csv_string = csv_string
        self.attendees = []
        self.unidentifiable = []
        self.datetime = None
        self.duration = None
        self.topic = None
        self.total_participants = None
        self.grade_level = None
        self.homeroom = None
        self.read_report()

    def __repr__(self):
        outstr = (
            f'<self.helper.zoom_attendance_report.Meeting; {self.topic} at '
            f'{self.datetime.isoformat()}>'
        )
        return outstr

    def __str__(self):
        return f'{self.datetime.isoformat()}; {self.topic}'

    def __eq__(self, other):
        # input validation
        if not isinstance(other, Meeting):
            try:
                outstr = (
                    'Unsupported operand; cannot compare type "Meeting" to '
                    + type(other)
                )
                raise ValueError(outstr)
            finally:
                raise ValueError('Unsupported operand')
        self_identifier = self.topic + self.datetime.isoformat()
        other_identifier = other.topic + other.datetime.isoformat()
        if self_identifier == other_identifier:
            return True
        return False

    def __gt__(self, other):
        # input validation
        if not isinstance(other, Meeting):
            try:
                outstr = (
                    'Unsupported operand; cannot compare type "Meeting" to '
                    + type(other)
                )
                raise ValueError(outstr)
            finally:
                raise ValueError('Unsupported operand')
        return len(self.attendees) > len(other.attendees)

    def __len__(self):
        return len(self.attendees)

    def read_report(self):
        """
        Reads, and parses zoom report

        assigns attributes:
        self.topic
        self.grade_level
        self.datetime
        """
        rows = []
        for line in self.csv_string.split('\n')[:-1]:
            line = line.strip()
            rows.append(line.split(','))
        # raise an exception if row 2 is not blank.
        # tolerate the case of row[2] = ['', '', '', ...]
        exception_message = (
            'Zoom report must contain meeting information. The report for '
            f'{self.topic} at {self.datetime} does not appear to contain '
            'meeting information.'
        )
        if rows[2]:
            rw = set(rows[2])
            if len(rw) <= 1:
                if rw.pop():
                    raise Exception(exception_message)
            else:
                raise Exception(exception_message)
        # parse the CSV, having cleared the exception check
        self.duration = int(rows[1][5])
        self.topic = rows[1][1]
        time_str = rows[1][2]
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

        # first pass; get the easy matches, determine the homeroom and grade
        # level if possible

        # first pass; get the easy matches, determine the homeroom and grade
        # level if possible
        grade_levels_within = set()
        homerooms_within = set()
        matched = []  # cached matched, skip on second pass
        for row in rows[4:]:
            st = self.helper.find_nearest_match(row[0], auto_yes=True)
            if not st:
                continue
            st.zoom_attendance_report.setdefault(
                self.__str__(),
                int(row[2])  # duration of attendance
            )
            matched.append(row[0])
            grade_levels_within.add(st.grade_level)
            homerooms_within.add(st.homeroom)

        # if the members of the group are all in a single homeroom or grade
        # level, we can narrow our search later.
        if len(grade_levels_within) <= 1:
            self.grade_level = grade_levels_within.pop()
        if len(homerooms_within) <= 1:
            self.homeroom = homerooms_within.pop()

        # second pass, use grade level knowledge to match difficult students.
        for row in rows[4:]:
            if row[0] in matched:
                continue
            st = self.match_student(row[0])
            if not st:
                self.unidentifiable.append(row[0])
                continue
            st.zoom_attendance_record.setdefault(
                self.__str__(),
                int(row[2])  # duration of attendance
            )
            self.attendees.append(st)

    def match_student(self, name):
        """
        Wrapper method that ties together the self.helper class's find_student
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
            # use helper search, which can raise warnings
            st = self.helper.find_nearest_match(name, auto_yes=True)
            if st:
                return st
        except Warning:
            pass
        # search whole name wthin subgroup
        st = self.try_matching_student_within_subgroup(name)
        if st:
            return st
        for part in [i for i in re.split(r'[ |.]', name) if i]:
            # search each word in name within subgroup
            st = self.try_matching_student_within_subgroup(part)
            if st:
                return st
            st = self.try_matching_student_within_subgroup(
                part, last_name=True)
            return st

    def try_matching_student_within_subgroup(self, student_name, last_name=False):
        """
        Unlike in the self.helper student matching function, this class is aware of
        the grade level of the student it is trying to match. If the self.helper
        method returns None, this fallback method tries to identify the
        student through process of elimination within their own grade. This
        helps match more students who only provide their first name.
        """
        if self.homeroom:  # preferentially search within homeroom
            compare_attr = 'homeroom'
        elif self.grade_level:  # fallback on grade level
            compare_attr = 'grade_level'
        else:
            return  # no subgroup to compare within
        name_part = 'last_name' if last_name else 'first_name'
        qs = [
            s.__dict__[name_part] for s in self.helper.students.values()
            if s.__dict__[compare_attr] == self.__dict__[compare_attr]
        ]
        first_name_match = process.extract(
            student_name,
            qs,
            limit=2
        )
        if first_name_match[0][1] > 90:
            # we have a potential match! Let's see if it's truly a match
            # first, re-extract the student object from all students...

            # If the best two matches are the same name, there are two or more
            # students in the grade level with that name. It is therefore
            # impossible to perform a perfect match against only the first name
            if first_name_match[1][0] == first_name_match[0][0]:
                logger.debug(
                    f'Cannot proceed with {student_name}. More than one '
                    f'student in the {self.grade_level}th grade has the first '
                    f'name {first_name_match[0][0]}.'
                )

            # If the first two matches are not the same, that means the first
            # name is unique, and we can make a match within the grade level.
            for n, s in self.helper.students.items():
                if n.split(' ')[0] == first_name_match[0][0]:
                    logging.debug(
                        'Successful grade level match for '
                        + self.helper.students[n].name
                    )
                    return self.helper.students[n]


class MeetingSet(HelperConsumer):
    """

    # General Usage

    A directory full of meeting reports can be carelessly tossed into
    __init__. This class dynamically groups meetings by attendees. For example,
    if you use the same meeting topic (i.e. "Health") to meet with different
    groups of homerooms throughout the week, this class will observe the union
    of the set of attendees at each meeting instance, and if there is a
    significant intersection, those meetings are grouped.

    # Resultant Data Structure

    Meeting groupings will be accessible as a nested list (self.groups).
    Each item in the list will itself be a chronologically sorted list of
    Meeting instances.

    The presumption is that there is no reliable way to know the full name of
    a meeting. For example, the meeting topic might be, "Health," but whoose
    homeroom is it? There's no way to know from here. Hence, this class simply
    takes a large pool of meetings and groups them. Labeling can be done
    elsewhere.

    The topics of each meeting are saved as an attribute on the
    meeting; "meeting.topic". It is possible for multiple meeting instances
    with the same topic to be split into different groups if the participants
    are different enough. This is expected such as in the example case detailed
    above. However, meetings with different topics will never be grouped
    together.

    If, for whatever reason, a teacher has meet with the same class under
    different zoom meet topics, that case could probably be dealt with in a
    more flexible subclass which modifies the "match_meeting_with_group_by_union"
    method.
    """

    def __init__(self, csv_strings: list, group_map=None, trust_topics=False):
        super().__init__()
        self.csv_strings = csv_strings
        self.groups = []
        self.meetings = []  # all meetings in a flattened list
        self.TOTAL_TO_UNION_RATIO_ADJUSTMENT = 0.8

        # init dict on student objects
        for st in self.helper.students.values():
            st.zoom_attendance_report = {}

    def process(self):
        """
        Generator that produces data structure. Yields a meeting immediately
        after it has been parsed.
        """
        for st in self.helper.students.values():
            st.zoom_attendance_record = {}
        # append all meetings to groupings in self.groups
        for csv_string in self.csv_strings:
            meeting = Meeting(csv_string)
            self.meetings.append(meeting)
            match = self.match_meeting_with_group_by_union(meeting)
            if match:
                match.append(meeting)
            else:
                self.groups.append([meeting])
            yield meeting  # report progress up the callstack.

    def match_meeting_with_group_by_union(self, meeting: Meeting):
        """
        Given a list of students, calculate the union between that list, and
        all the other lists of students in meetings previously provided.

        Return the group whose union against the provided list is less than the
        length of the lists combined, indicating that these are two instances
        of the same group of students meeting.
        """
        for group in self.groups:
            # select closest_meeting: the past meeting whose len() is closest
            # to the current meeting.
            closest_meeting = None
            smallest_difference = 100  # initialize with random large number
            for prev_meeting in group:
                diff = abs(len(prev_meeting) - len(meeting))
                if diff < smallest_difference:
                    smallest_difference = diff
                    closest_meeting = prev_meeting

            # perform set union comparison
            cm__attendees = {s.name for s in closest_meeting.attendees}
            m__attendees = {s.name for s in meeting.attendees}
            union = len(cm__attendees | m__attendees)
            total = len(cm__attendees) + len(m__attendees)
            # MATCH CRITERIA
            matched = total > union and prev_meeting.topic == meeting.topic
            if matched:
                logging.debug(matched)
                return group
        return []


class DynamicDateColorer:
    """
    Class meetings after October 4, 2020 changed from 30 to 45 minutes.
    Hence, the coloring of cells needs to be responsive.
    """

    def __init__(self, *a, **kw):
        # define constants
        self.OCTOBER_4_2020 = 1601769600  # timestamp
        self._30_MIN_GREEN = 25
        self._30_MIN_YELLOW = 18
        self._45_MIN_GREEN = 40
        self._45_MIN_YELLOW = 30

        def fill(colorcode):
            return PatternFill(
                fill_type='solid',
                start_color=colorcode,
                end_color=colorcode
            )

        self.colors = {
            'green': fill('18fc03'),
            'yellow': fill('fcf403'),
            'red': fill('fc0303'),
        }

    def get_color(self, duration: int, timestamp: int):
        if timestamp < self.OCTOBER_4_2020:
            return self._30_min_class_color(duration)
        return self._45_min_class_color(duration)

    def _30_min_class_color(self, duration):
        if duration > self._30_MIN_GREEN:
            return self.colors.get('green')
        if duration > self._30_MIN_YELLOW:
            return self.colors.get('yellow')
        return self.colors.get('red')

    def _45_min_class_color(self, duration):
        if duration > self._45_MIN_GREEN:
            return self.colors.get('green')
        if duration > self._45_MIN_YELLOW:
            return self.colors.get('yellow')
        return self.colors.get('red')

    def get_color_avg(self, duration):
        if duration > 30:
            return self.colors.get('green')
        if duration > 15:
            return self.colors.get('yellow')
        return self.colors.get('red')


class WorkbookWriter(DynamicDateColorer):
    """
    Writes a MeetingSet into an excel report

    Dynamically Grouped Sheet:
        The master sheet contains a summary of all data in one place.
        Students are listed from top to bottom by dynamic grouping,
        and each meeting date gets a column to the right of the student
        name column which shows the students minutes of attendance and is

    All Students Sheet:
        All students regardless of whether they ever attended a zoom
        meeting with an ov
        Each group gets its own sheet for its attendance.

    Highlights Sheet(s):
        Gives some helpful highlights:
            - Students in the top and bottom 10th percentile of attendance
                across all groups.
            - Group with the best & worst attendance (this is only measured
                against the historical max attendance for that group, since
                the total size of the group is unknown)
            - Students whose name could not be matched. Some students use
                weird names. This program ignores those students if they
                are truly unidentifiable, but they get dumped onto the
                highlight sheet so you can at least see how many anonymous
                students there are, and what names they are using.
    """

    def __init__(self, meeting_set: MeetingSet, *a, **kw):
        super().__init__()
        self.meeting_set = meeting_set
        self.thresholds = kw.get('attendance_duration_thresholds')
        # init workbook
        self.workbook = Workbook()
        self.workbook.remove(self.workbook.active)
        self.styles = {
            'h1': Font(size=30, bold=True, name='Cambria'),
            'h2': Font(size=16, name='Calibri')
        }
        self.sheet_writer_classes = [
            MainSheetWriter,
            ListByHomeroomSheetWriter,
            HighlightSheetWriter
        ]

    def generate_report(self) -> Workbook:
        """
        Call funcs below to generate each sheet, then return the workbook.
        """
        # write sheets
        for SheetWriter in self.sheet_writer_classes:
            wr = SheetWriter(self.meeting_set, self.workbook.create_sheet())
            wr.write_sheet()

        return self.workbook

    def write_main_sheet_key_with_dynamic_colors(self, sheet):
        """
        This is kind of graveyard code because I gave up on drilling down
        dynamically assigned colors. But, I'm preserving it because it might
        be re-added in the future.

        Note that this writes the main sheet up to row 4 (1-based index)
        """
        sheet.page_setup.fitToWidth = 1
        # header information
        a1 = sheet['A1']
        a1.value = 'Zoom Attendance Report'
        a1.font = self.styles['h1']
        b1 = sheet['A2']
        b1.value = 'Key'
        b1.font = self.styles['h2']

        # fill in key
        b2, c2 = sheet['A3':'B3'][0]
        b2.fill = self.colors['green']
        c2.value = (
            f'Green: Student attended for at least {self._30_MIN_GREEN} '
            f'minutes before 10/4/2020, or {self._45_MIN_GREEN} after '
            '10/4/2020.'
        )
        b3, c3 = sheet['A4':'B4'][0]
        b3.fill = self.colors['yellow']
        c3.value = (
            f'Yellow: Student attended for at least {self._30_MIN_YELLOW} '
            f'minutes before 10/4/2020, or {self._45_MIN_GREEN} after '
            '10/4/2020.'
        )
        b4, c4 = sheet['A5':'B5'][0]
        b4.fill = self.colors['red']
        c4.value = (
            'Red: Student attended for less than {self._30_MIN_YELLOW} before '
            f' 10/4/2020, or {self._45_MIN_YELLOW} after 10/4/2020.'
        )


class BaseSheetWriter(DynamicDateColorer):
    def __init__(
            self,
            meeting_set: MeetingSet,
            sheet,
            start_row=1,
            title='Sheet'
    ):
        super().__init__()
        self.meeting_set = meeting_set
        self.sheet = sheet
        self.groups = meeting_set.groups
        self.sheet.title = title
        self.cur_row = start_row

    def write_sheet(self):
        """
        Write data into the sheet provided to init.
        """
        raise NotImplementedError

    def write_cell(self, *,
                   value: str, row=None, col: int, font=None, fill=None
                   ):
        """
        Utility for writing to a single cell with styles. Does not incremenet
        self.cur_row.
        """
        row = row if row else self.cur_row          # override default row value
        cell = self.sheet.cell(row=row, column=col)  # select column
        cell.value = value                          # write value
        if font:                                    # set font
            cell.font = font
        if fill:                                    # set fill
            cell.fill = fill


class MainSheetWriter(BaseSheetWriter):
    """
    Note that this class does not support dynamic coloring, it uses the
    constants defined in ExcelStyles above.
    """

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw, title='Main')

        self.cur_group = []
        self.cur_group_students = []
        self.cur_headers = []

        # map of meeting header strings to their timestamp, for later.
        self.name_to_timestamp_map = {
            m.__str__(): m.datetime.timestamp() for m in self.meeting_set.meetings
        }

    def write_sheet(self):
        """
        Orchestrate private functions below.
        """
        for group in self.groups:
            self.cur_group = group

            # get all students from the group
            students = set()
            for meeting in group:
                meet_students = set(meeting.attendees)
                students.update(meet_students)
            self.cur_group_students = students

            self._write_group_headers()
            self._write_rows()
            self.cur_row += 2  # leave 2 blank rows between groups

    def _write_group_headers(self):
        """
        For each group, write a row of headers that describe each meeting the
        group had.
        """
        group_topics = ' ,'.join(
            topic_set := {t.topic for t in self.cur_group})
        temp = self.sheet.cell(row=self.cur_row, column=1)
        s = 's' if len(topic_set) > 1 else ''  # plurality
        temp.value = 'Dynamic Group'
        temp.font = Font(size=32, bold=True)

        self.cur_row += 1

        temp = self.sheet.cell(row=self.cur_row, column=1)
        temp.value = f'Group contains meet topic{s}: {group_topics}'
        temp.font = Font(size=24, italic=True)

        self.cur_row += 1

        # write the last header row: column labels
        self.cur_group.sort(key=lambda m: m.datetime)
        self.cur_headers = [m.__str__() for m in self.cur_group]
        write_headers = ['Last Name', 'First Name'] + self.cur_headers
        for i, topic in enumerate(write_headers):
            i += 1  # 1-based index for openpyxl
            cell = self.sheet.cell(row=self.cur_row, column=i)
            cell.value = topic.title()
            cell.font = Font(bold=True)
        self.cur_row += 1

    def _write_rows(self):
        """
        Write row for each student.
        """
        students = list(self.cur_group_students)
        students.sort(key=lambda s: s.last_name)
        for student in students:
            # write student name
            last_name_cell = self.sheet.cell(row=self.cur_row, column=1)
            last_name_cell.value = student.last_name
            last_name_cell.font = Font(size=16)
            first_name_cell = self.sheet.cell(row=self.cur_row, column=2)
            first_name_cell.font = Font(size=16)
            first_name_cell.value = student.first_name

            # iterate over headers to fill in row
            for i, header in enumerate(self.cur_headers):

                # select cell
                i += 3  # offset for first and last name
                cell = self.sheet.cell(row=self.cur_row, column=i)
                cell.font = Font(size=16)

                # select value
                mins_attended = student.zoom_attendance_record.get(header)
                if not mins_attended:
                    mins_attended = 0

                # assign value to cell
                cell.value = mins_attended

                # color cell
                cell.fill = self.get_color(
                    mins_attended,
                    self.name_to_timestamp_map[header]
                )
            self.cur_row += 1


class ListByHomeroomSheetWriter(BaseSheetWriter, HelperConsumer):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw, title='Attendance Summary by Homeroom')

    def write_sheet(self):
        self._write_sheet_header()
        self.cur_row += 2
        for homeroom in self.helper.homerooms.values():
            self._write_homeroom_header(homeroom)
            self.cur_row += 1
            for student in homeroom.students:
                self._write_homeroom_student(student)
                self.cur_row += 1
            self.cur_row += 2

    def _write_sheet_header(self):
        """
        Header for the whole sheet.
        """
        # title
        temp = self.sheet.cell(row=self.cur_row, column=1)
        temp.value = 'Attendance Summary by Homeroom'
        temp.font = Font(bold=True, size=32)
        self.cur_row += 1

        # description
        temp = self.sheet.cell(row=self.cur_row, column=1)
        temp.value = (
            'An overview of all students sorted by homeroom, regardless '
            'of whether they\'ve ever actually attended your meeting.'
        )
        self.cur_row += 1

        # key
        temp = self.sheet.cell(row=self.cur_row, column=1)
        temp.value = 'Key'
        temp.font = Font(size=24)
        self.cur_row += 1

        # key rationale
        temp = self.sheet.cell(row=self.cur_row, column=1)
        temp.value = (
            'We spent 4 weeks @ 30min / wk, and 6 weeks at 45 min / wk so '
            'far. With that in mind, we would expect the perfect student '
            'to have an average meeting attendance duration of 39 minutes. '
            'bearing that in mind...'

        )
        self.cur_row += 1

        # key__green
        temp_color = self.sheet.cell(row=self.cur_row, column=1)
        temp_color.fill = self.colors['green']
        temp_label = self.sheet.cell(row=self.cur_row, column=2)
        temp_label.value = (
            'Average attendance duration is greater than 30 minutes.'
        )
        self.cur_row += 1

        # key__yellow
        temp_color = self.sheet.cell(row=self.cur_row, column=1)
        temp_color.fill = self.colors['yellow']
        temp_label = self.sheet.cell(row=self.cur_row, column=2)
        temp_label.value = (
            'Average attendance duration is greater than 15 minutes.'
        )
        self.cur_row += 1

        # key__red
        temp_color = self.sheet.cell(row=self.cur_row, column=1)
        temp_color.fill = self.colors['red']
        temp_label = self.sheet.cell(row=self.cur_row, column=2)
        temp_label.value = (
            'Average attendance duration is less than 15 minutes.'
        )
        self.cur_row += 1

    def _write_homeroom_header(self, homeroom):
        """
        Header for each homeroom.
        """
        temp = self.sheet.cell(row=self.cur_row, column=1)
        temp.value = homeroom.teacher
        temp.font = Font(size=20)

        headers = [
            'Last Name',
            'First Name',
            'Average Attendance',
            'Total Meetings Attended',
        ]
        for i, h in enumerate(headers):
            temp = self.sheet.cell(row=self.cur_row, column=i + 1)
            temp.value = h
            temp.font = Font(bold=True, size=16)

    def _write_homeroom_student(self, student):
        """
        Write one row, corresponding to one student.
        """
        zar = student.__dict__.get('zoom_attendance_record')
        row = [
            student.first_name,
            student.last_name,
            self._calc_avg_attendance(zar),
            len(zar) if zar else 0
        ]
        color = self.get_color_avg(row[2])
        for i, val in enumerate(row):
            temp = self.sheet.cell(row=self.cur_row, column=i + 1)
            temp.value = val
            temp.font = Font(size=16)
            temp.fill = color

    @ staticmethod
    def _calc_avg_attendance(zoom_attendance_report: dict) -> int:
        return (
            (
                sum(zoom_attendance_report.values())
                / len(zoom_attendance_report)
            )
            if zoom_attendance_report else 0
        )


class HighlightSheetWriter(BaseSheetWriter):

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw, title='Highlights')

    def write_sheet(self):
        self._write_sheet_header()
        self._write_missing_students()

    def _write_sheet_header(self):
        self.write_cell(
            value='Highlights',
            col=1,
            font=Font(size=32, bold=True),
        )
        self.cur_row += 2

        self.write_cell(
            value='Unmatched Names',
            col=1,
            font=Font(size=24, bold=True)
        )
        self.cur_row += 1

        self.write_cell(
            value=(
                'This report is not perfect. As you very well know, many '
                'students use names in zoom calls that have no relationship '
                'to their real name. You had an opportunity to manually match '
                'some of these names back in the web interface, but even a '
                'human can\'t necessecarily reliably match these names. '
            ),
            col=1,
        )
        self.cur_row += 1

        self.write_cell(
            value=(
                'Nevertheless, the names are stored here for your reference, '
                'and so that you have a sense of how many students are missing '
                'from the rest of this report.'
            ),
            col=1,
        )
        self.cur_row += 1

    def _write_missing_students(self):
        unidentifiable = set()
        for group in self.groups:
            for meeting in group:
                unidentifiable.update(meeting.unidentifiable)
        start_block = copy(self.cur_row)
        cur_col = 1
        n = len(unidentifiable) // 10
        for i, name in enumerate(unidentifiable):
            i += 1
            # every n rows, move one column over and fill the same row range
            # again. n is porportional to len(unidentifiable) to make a nice block.
            if not i % n:
                cur_col += 1
                self.cur_row = copy(start_block)

            self.cur_row += 1

            # write name to current cell
            self.write_cell(
                row=self.cur_row,
                col=cur_col,
                value=name
            )
