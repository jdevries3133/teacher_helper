import dbm
import os
import shelve
from copy import copy
from datetime import datetime

from fuzzywuzzy import process

from .HelperMixins import EndOfSchoolYearMixin, OnCourseMixin, SillyMixin
from .student import Student

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

    def find_nearest_match(self, student_name, auto_yes=False, threshold=90, **kwargs):
        """
        Returns a student object. If auto_yes=True, it will presume that the
        best matching student is correct. Optionally, set a levenshtien distance
        threshold below which students will not be included.
        """
        if isinstance(student_name, list):
            return self.find_nearest_match_depr(student_name, auto_yes, **kwargs)
        if not isinstance(student_name, str):
            raise TypeError("Student name must be passed as a string")
        if not len(student_name.split(' ')) > 1:
            raise Warning(
                'find_nearest_match will typically return an incorrect result '
                'if student\'s full name is not provided.'
            )
        try:
            # exact match
            return self.students[student_name]
        except KeyError:
            pass
        closest_name, confidence = process.extractOne(
            student_name,
            self.students.keys()
        )
        if auto_yes:
            res = True
        else:
            print('Do these names match? (y/n)')
            print('-' * 80)
            print(student_name, closest_name, sep='\t', end="\n\n")
            res = input()
            if res.lower() in ['y', 'yes']:
                res = True
            elif res.lower() in ['n', 'no']:
                res = False
            else:
                print('Please enter "y" or "n".')
                self.find_nearest_match(student_name)
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

    def find_nearest_match_depr(self, student_names, auto_yes=False, **kwargs):
        """
        Takes a list of student names, and returns a list of student objects
        from self.students. If there is no exact name match, it will perform a 
        fuzzy match and ask the user to resolve the ambiguity in the command line.

        If altTab is true, it will assume this is part of a gui script, and 
        "command-tab" the user in and out of the input 
        """
        raise Exception('remove depricated function')
        # deprication compatibility
        if kwargs.get('debug'):
            auto_yes = kwargs['debug']
        for index, name in enumerate(copy(student_names)):
            # direct match(es)
            matches = [(s.name, s) for s in self.students if s.name == name]
            if matches:
                # single direct match
                if len(matches) == 1:
                    student_names[index] = matches[0][1]
                # multiple matches
                else:
                    for match in matches:
                        done = False
                        if not auto_yes:
                            print('-' * 80)
                            print(
                                '\nDo these names match? (y/n/p) (yes, no, pass)\n')
                            print(name + '\t' + match[0] + '\n')
                        while True:
                            if auto_yes:
                                yn = 'y'
                            else:
                                yn = input().lower()
                            if yn == 'y':
                                student_names[index] = match[1]
                                break
                            elif yn == 'n':
                                break
                            elif yn == 'p':
                                pass
                            else:
                                print('Please enter y, n, or p')
                        if done:
                            break
            # no match
            else:
                qset = process.extractOne(
                    name,
                    [s.name for s in self.students]
                )
                if not auto_yes:
                    print('-' * 80)
                    print('\nDo these names match? (y/n/p) (yes, no, pass)\n')
                while True:
                    if auto_yes:
                        u_in = 'y'
                    else:
                        u_in = input(name + '\t' + qset[0] + '\n').lower()
                    if u_in == 'y':
                        student_names[index] = (
                            [s for s in self.students if s.name == qset[0]][0]
                        )
                        break
                    elif u_in == 'n':
                        break
                    elif u_in == 'p':
                        break
                    else:
                        print('Please enter "y" or "n."')
        for name in copy(student_names):
            if not isinstance(name, Student):
                print(f'{name} was deleted because they had no match.')
                student_names.remove(name)
        return student_names  # now converted to Student class instances

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
            shelve.open(os.path.join(MODULE_DIR, 'cache'), 'r')
            return True
        except dbm.error:
            return False
