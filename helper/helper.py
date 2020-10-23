import os
import dbm
import shelve
from datetime import datetime

from fuzzywuzzy import process

from .HelperMixins import EndOfSchoolYearMixin, OnCourseMixin, SillyMixin

MODULE_DIR = os.path.dirname(__file__)


class Helper(
        EndOfSchoolYearMixin,
        OnCourseMixin,
        SillyMixin,):
    """
    Driver for the entire module! See README.md test
    """

    def __init__(self, homerooms=None, students=None, groups=None):
        for i in [homerooms, students, groups]:
            if i and not isinstance(i, dict):
                raise Exception()
        super().__init__(homerooms, students, groups)
        self.homerooms = homerooms
        self.students = students
        self.groups = groups
        self.cache_dir = os.path.join(__file__, 'cache')

    def write_cache(self):
        with shelve.open(os.path.join(MODULE_DIR, 'cache'), 'c') as db:
            db['data'] = self
            db['date'] = datetime.now()

    def find_nearest_match(self, student_name: str, auto_yes=False, threshold=90, **kwargs):
        """
        Returns a student object. If auto_yes=True, it will presume that the
        best matching student is correct. Optionally, set a levenshtien distance
        threshold below which students will not be included.
        """
        if not len(student_name.split(' ')) > 1 and auto_yes:
            """
            print(
                'WARNING: If a student\'s full name is not provided, the query result '
                'will likely have a low confidence and not pass the default '
                'threshold value of 90. Lowering the threshold value will '
                'greately increase the liklehood of incorrect matches. '
                'Hence, it is best to provide the student\'s full name to this '
                'function if auto_yes is set to true.\n\tThe name provded was:\t'
                + student_name
            )
            """
        # direct match
        if st := self.students.get(student_name.title()):
            return st
        closest_name, confidence = process.extractOne(
            student_name,
            self.students.keys()
        )
        if auto_yes:
            res = True
        else:
            res = self.match_in_terminal(student_name, closest_name)
        if res and not auto_yes:
            # allow match to pass regardless of threshold if match was provided
            # by user input
            return self.students[closest_name]
        if res and auto_yes:
            if confidence > threshold:
                return self.students[closest_name]
        if not auto_yes:  # provide feedback to user
            print('Student object not found. find_nearest_match will return None')
        # None will be returned if no return conditions are met

    def match_in_terminal(self, a, b):
        print('Do these names match? (y/n)')
        print('-' * 80)
        print(a, b, sep='\t', end="\n\n")
        res = input()
        if res.lower() in ['y', 'yes']:
            return True
        elif res.lower() in ['n', 'no']:
            return False
        else:
            print('Please enter "y" or "n".')
            return self.match_in_terminal(a, b)

    @ staticmethod
    def read_cache(check_date=True):
        """
        This static method returns a class because I like to break the rules.
        there's a reason for the rules; this garbage doesn't work
        """
        with shelve.open(os.path.join(MODULE_DIR, 'cache'), 'r') as db:
            data = db['data']
            date = db['date']
        if check_date and (datetime.now().month in range(9, 12) and date.month in range(1, 7)):
            raise Exception(
                'It appears that the cache is from last school year. Please\n'
                'provide new data, re-instantiate, and re-write cache.'
            )
        return data

    @ staticmethod
    def cache_exists():
        try:
            sh = shelve.open(os.path.join(MODULE_DIR, 'cache'), 'r')
            sh.close()
            return True
        except dbm.error:
            return False
