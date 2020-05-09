from copy import copy
import csv
from datetime import datetime
import os
from pathlib import Path
import shelve
import itertools  # use to return iterators for different scenarios

from fuzzywuzzy import process

from .csv_parsers import parse_homeroom, parse_group
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

        # students missing a student id
        st_mis = [s for s in self.students if not s.student_id]

        # students who have a student id
        good_sts = [s for s in self.students if s.student_id]

        # for each student without an id
        for st in st_mis:

            # find the nearest match in the list of students who have ids
            qset = process.extractOne(st.name, [s.name for s in good_sts])

            # ask user to verify match
            print('\nDo these names match? (y/n)\n')
            u_in = input(st.name + '\t' + qset[0] + '\n').lower()

            # only accept 'y' or 'n'
            while True:

                # assign some attributes of the id-rich student to the id-lacking
                # one. Usually, bad id matches are due to nicknames, so this sort
                # of merges these student instances.
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
                homeroom = parse_homeroom(path_to_csv)

                homerooms.append(homeroom)
                for st in copy(homeroom.students):
                    if st.student_id in [s.student_id for s in students]:
                        match = Helper.get_matching_student(st, students, homeroom.teacher)
                        homeroom.students.remove(st)
                        homeroom.students.append(match)
                    else:
                        students.append(st)

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

                group = parse_group(path_to_csv)
                for st in copy(group.students):
                    if st.name in [s.name for s in students]:
                        match = Helper.get_matching_student(st, students)
                        match.groups += group.name
                        group.students.remove(st)
                        group.students.append(match)
                    else:
                        students.append(st)

                groups.append(group)

        for st in students:
            if not st.student_id:
                print(f'WARN: No student id for {st.name}')

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




