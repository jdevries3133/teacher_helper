from copy import copy
import csv
from datetime import datetime
import os
from pathlib import Path
import shelve

from fuzzywuzzy import process

from .csv_parsers import (
    parse_homeroom,
    parse_group,
    nonparticipator_audit_flipgrid,
)
from .json_parsers import assignment_participation_audit
from .group import Group
from .homeroom import Homeroom
from .student import Student

class Helper:
    def __init__(self, homerooms=None, students=None, groups=None):
        self.homerooms = homerooms
        self.students = students
        self.groups = groups

    def write_cache(self):
        with shelve.open('cache', 'c') as db:
            db['data'] = self
            db['date'] = datetime.now()

    def read_emails_from_csv(self, path):
        with open(path, 'r') as csvfile:
            rd = csv.reader(csvfile)
            for row in rd:
                for st in self.students:
                    if st.student_id == row[0]:
                        st.email = row[1]

    def resolve_missing_st_id(self):
        """
        Iterate through students who have no student ID. Perform a fuzzy match
        on the pool of students, and ask the user if it is a match. No-ID case
        often arises if a group list is imported with nicknames. Often, student
        ID's are critical for LMS endpoints.

        For now, if the user says "n," the student is just deleted. Obviously
        the assumption is that students who are not part of the school are not
        in any groups. This function must be modified to handle students who are
        group members that are not students in the school.
        """

        st_mis = [s for s in self.students if not s.student_id]
        good_sts = [s for s in self.students if s.student_id]
        for st in st_mis:
            qset = process.extractOne(st.name, [s.name for s in good_sts])
            print('\nDo these names match? (y/n)\n')
            u_in = input(st.name + '\t' + qset[0] + '\n').lower()
            # only accept 'y' or 'n'
            while True:

                if u_in == 'y':
                    st_good = [s for s in good_sts if s.name == qset[0]][0]
                    st.student_id = st_good.student_id
                    st.name = st_good.name
                    st.__dict__.setdefault('homeroom', st_good.homeroom)
                    break

                # delete the student; if they have no id-bearing match,
                # they probably moved away
                if u_in == 'n':
                    self.students.remove(st)
                    break

                # only accept "y" or "n"
                else:
                    print('Please enter "y" or "n"')

        # make sure that every student now has an ID; critical for genesis
        # API endpoints.
        if [s for s in self.students if not s.student_id]:
            raise Exception("Didn't handle all missing student id's")

        return self.students

    def find_non_participators(self, directories):
        """
        Opens every file in each of the passed directories (csv or json), and
        identfies assignments as:

            Google classroom json exports
            Flipgrid csv exports
            Edpuzzle csv exports

        Then, the function writes overall participation data to a conditionally
        formatted excel file with openpyxl.
        """

        # give each assignment a unique id.
        # maintain a dictionary of assignments, where the UUID is the key, and
        # the value is a dictionary with keys "NAME", and "DATE"

        self.assignments = {}
        for st in self.students:

            """
            this dict will have keys:

                assignment_id: str
                assignment_completed: bool
            """
            st.assignments = {}

        for direc in directories:
            for file_path in direc.iterdir():

                # check for mac bs
                if '.csv' not in file_path.name:
                    if '.json' not in file_path.name:
                        continue

                # route file
                if direc.name == 'google_classrooms':
                    assignment_participation_audit(file_path, self)
                if direc.name == 'flipgrid':
                    continue
                    nonparticipator_audit_flipgrid(file_path, self)
                if direc.name == 'edpuzzle':
                    continue
                    nonparticipator_audit_edpuzzle(file_path, self)
        breakpoint()

    @classmethod
    def new_school_year(cls, csvdir):
        """
        Pass an absolute path to a directory full of csv files for all homerooms
        and miscellaneous groups. Note that these CSV files must follow a
        fairly strict naming convention as described in this module's readme.
        """
        homerooms = []
        students = []
        groups = []


        # deal with all homerooms, pass over groups
        for filename in os.listdir(csvdir):

            # skip .DS_store and other nonsense
            if '.csv' not in filename:
                continue

            path_to_csv = Path(csvdir, filename)

            # call parsing functions
            if path_to_csv.stem[0] == 'h':
                teacher, grade_level, this_students = parse_homeroom(path_to_csv)
                for st in copy(this_students):
                    if st.student_id in [s.student_id for s in students]:
                        match = Helper.get_matching_student(st, students, homeroom.teacher)
                        this_students.remove(st)
                        this_students.append(match)
                    else:
                        students.append(st)

                homeroom = Homeroom(teacher, grade_level, this_students)
                homerooms.append(homeroom)
                print('homeroom', homeroom.teacher, 'has', str(len(homeroom.students)), 'students')

            elif path_to_csv.stem[0] == 'g':
                # deal with groups once all the homerooms are done to help
                # with the duplicate student problem
                continue

            else:
                raise Exception(f'Unable to parse file: {filename}')

        for filename in os.listdir(csvdir):

            # skip .DS_store and other nonsense
            if '.csv' not in filename:
                continue

            path_to_csv = Path(csvdir, filename)

            if path_to_csv.stem[0] == 'g':

                name, grade_level, this_students = parse_group(path_to_csv)
                for st in copy(this_students):
                    if st.name in [s.name for s in students]:
                        match = Helper.get_matching_student(st, students)
                        match.groups += st.groups
                        this_students.remove(st)
                        this_students.append(match)
                    else:
                        students.append(st)

                group = Group(name, grade_level, this_students)
                groups.append(group)



        return cls(homerooms, students, groups)

    @staticmethod
    def get_matching_student(st, students, append_homeroom=None):
        """
        Look through the list of students. Find and return the already parsed
        instance of that student so that they can be linked to this new context.

        Some students are in two homerooms for some reason, so if this function
        is called in the homeroom parsing code block, the append_homeroom
        argument should be whatever homeroom is currently being parsed. That
        homeroom will be added to the student instance as st.alt_homeroom.
        """

        for st_match in students:
            if st.student_id:
                if st_match.student_id == st.student_id:
                    if append_homeroom:
                        st_match.alt_homeroom = append_homeroom
                        return st_match
                    else:
                        return st_match

            elif st.name:
                if st.first_name == st_match.first_name and st.last_name == st_match.last_name:
                    if append_homeroom:
                        st_match.alt_homeroom = append_homeroom
                        return st_match
                    else:
                        return st_match


        raise Exception(
            f'Match for {st.name} not found. Only call this function if you '
            'are sure that there is a matching student in the list passsed as '
            'the second argument.'
        )


    @staticmethod
    def read_cache():
        """
        This static method returns a class because I like to break the rules.
        there's a reason for the rules; this garbage doesn't work
        """
        with shelve.open('cache', 'r') as db:
            data = db['data']
            date = db['date']

        if datetime.now().month in range(9, 12) and date.month in range(1, 7):
            raise Exception(
                'It appears that the cache is from last school year. Please\n'
                'provide new data, re-instantiate, and re-write cache.'
            )

        return data




