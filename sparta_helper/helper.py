from copy import copy
import csv
from datetime import datetime
import os
from pathlib import Path
import shelve
import itertools  # use to return iterators for different scenarios

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
            db['data'] = self.__dict__
            db['date'] = datetime.now()

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

        # iterate through every csv of various types of student lists, respond
        # to flags as per the readme.
        for filename in os.listdir(csvdir):

            # skip .DS_store and other nonsense
            if '.csv' not in filename:
                continue

            path_to_csv = Path(csvdir, filename)

            # call parsing functions
            if path_to_csv.stem[0] == 'h':
                homeroom = parse_homeroom(path_to_csv)
                homerooms.append(homeroom)
                students += [st for st in homeroom.students if st.name not in [s.name for s in students]]

            elif path_to_csv.stem[0] == 'g':
                pass
            elif path_to_csv.stem[0] == 'ph':
                group = parse_group(path_to_csv)
                groups.append(group)
                names_already_added = [st.name for st in students]

                for st in copy(group.students):
                    if st.name in names_already_added:
                        group.students.remove(st)
                        replacement = [s for s in students if s.name == st.name][0]
                        group.students.append([s for s in students if s.name == st.name][0])
                    else:
                        students.append(st)

            else:
                raise Exception(f'Unable to parse file: {filename}')

        return cls(homerooms, students, groups)

    @classmethod
    def read_cache(cls):
        """
        This static method returns a class because I like to break the rules.
        """
        with shelve.open('cache', 'r') as db:
            clsdict = db['data']
            date = db['date']

        if datetime.now().month in range(9, 12) and date.month in range(1, 7):
            raise Exception(
                'It appears that the cache is from last school year. Please\n'
                'provide new data, re-instantiate, and re-write cache.'
            )

        return cls(clsdict['homerooms'], clsdict['students'], clsdict['groups'])




