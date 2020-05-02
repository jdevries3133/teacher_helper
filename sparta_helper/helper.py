from datetime import datetime
import shelve
import itertools

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
        fairly strict naming convention.
        """


    @staticmethod
    def read_cache():
        with shelve.open('cache', 'r') as db:
            cls = db['data']
            date = db['date']

        if datetime.now().month in range(9, 12) and date.month in range(1, 7):
            raise Exception(
                'It appears that the cache is from last school year. Please\n'
                'provide new data, re-instantiate, and re-write cache.'
            )

        return cls






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

        self.students = []
        with open(csv_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            # instantiate a student for every student in the csv
            self.students = []
            row_check_re = re.compile(r'\d\d\d')
            for row in reader:
                if not re.search(row_check_re, row[0]):
                    continue

                # use re to get first and last name from "last_name, firt_name"
                inverted_name = row[1]
                match = re.search(re.compile(r','), inverted_name)
                flip_index = match.span()[0]
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
