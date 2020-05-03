import csv
from datetime import datetime
import os
import shelve
import itertools  # use to return iterators for different scenarios

from homeroom import Homeroom
from student import Student

class Helper:
    def __init__(self, homerooms=None, students=None, groups=None):
        self.homerooms = homerooms
        self.students = students
        self.groups = groups

    def write_cache(self):
        with shelve.open('cache', 'w') as db:
            db['data'] = self
            db['date'] = datetime.now()

    @classmethod
    def new_school_year(cls, csvdir):
        """
        Pass an absolute path to a directory full of csv files for all homerooms
        and miscellaneous groups. Note that these CSV files must follow a
        fairly strict naming convention as described in this module's readme.
        """
        for path in os.listdir(csvdir):
            print(path)
            continue
            if csvdir:
                self.teacher = csv_filename[1:-4]
                self.grade_level = csv_filename[0]

                # student names and ID's in the csv
                ID_HEADER_STRING = 'ID'
                NAME_HEADER_STRING = 'Name'

                # assign indicies of id and name rows to variables "id_index" and "name
                # index."
                with open(csv_path, 'r') as csv_file:
                    reader = csv.reader(csv_file)
                    students = []
                    id_index, name_index, = None, None
                    while not (id_index or name_index):
                        for row in reader:
                            for index, item in enumerate(row):
                                if item == 'ID':
                                    id_index = index
                                if item == 'Name':
                                    name_index = index

                # instantiate a student for every student in the csv
                self.students = []
                with open(csv_path, 'r') as csv_file:
                    reader = csv.reader(csv_file)
                    self.students = []
                    for row in reader:
                        inverted_name = row[1]
                        flip_index = inverted_name.index(',')
                        last_name = inverted_name[:flip_index]
                        first_name = inverted_name[(flip_index + 2):]

                        context = {
                            'first_name': first_name,
                            'last_name': last_name,
                            'student_id': int(row[0]),
                            'email': None,
                            'homeroom': csv_filename[1:-4],
                            'grade_level': csv_filename[0],
                        }

                        self.students.append(Student(context))

    @staticmethod
    def read_cache():
        """
        This static method returns a class because I like to break the rules.
        """

        with shelve.open('cache', 'r') as db:
            cls = db['data']
            date = db['date']

        if datetime.now().month in range(9, 12) and date.month in range(1, 7):
            raise Exception(
                'It appears that the cache is from last school year. Please\n'
                'provide new data, re-instantiate, and re-write cache.'
            )

        return cls




