from copy import copy
from datetime import datetime
import dbm
import os
import shelve

from fuzzywuzzy import process

from .student import Student
from .HelperMixins import (
    EndOfSchoolYearMixin,
    OnCourseMixin
)

MODULE_DIR = os.path.dirname(__file__)


class Helper(
        EndOfSchoolYearMixin,
        OnCourseMixin
    ):
    """
    Driver for the entire module! See README.md
    """
    def __init__(self, homerooms=None, students=None, groups=None):
        super().__init__(homerooms, students, groups)
        self.homerooms = homerooms
        self.students = students
        self.groups = groups
        self.cache_dir = os.path.join(__file__, 'cache')

    def write_cache(self):
        with shelve.open(os.path.join(MODULE_DIR, 'cache'), 'c') as db:
            db['data'] = self
            db['date'] = datetime.now()

    def find_nearest_match(self, student_names, auto_yes=False, **kwargs):
        """
        Takes a list of student names, and returns a list of student objects
        from self.students. If there is no exact name match, it will perform a 
        fuzzy match and ask the user to resolve the ambiguity in the command line.

        If altTab is true, it will assume this is part of a gui script, and 
        "command-tab" the user in and out of the input 
        """
        # deprication compatibility
        if 'debug' in kwargs:
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
                            print('\nDo these names match? (y/n/p) (yes, no, pass)\n')
                            print(name + '\t' + match[0] + '\n')
                        while True:
                            if auto_yes:
                                yn = 'y'
                            else:
                                yn = input().lower()
                            if yn == 'y':
                                student_names[index] = match[1]
                                break
                                done = True
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
                qset = process.extractOne(name, [s.name for s in self.students])
                if not auto_yes:
                    print('-' * 80)
                    print('\nDo these names match? (y/n/p) (yes, no, pass)\n')
                while True:
                    if auto_yes:
                        u_in = 'y'
                    else:
                        u_in = input(name + '\t' + qset[0] + '\n').lower()
                    if u_in == 'y':
                        student_names[index] = [s for s in self.students if s.name == qset[0]][0]
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

    @staticmethod
    def read_cache(check_date=True):
        """
        This static method returns a class because I like to break the rules.
        there's a reason for the rules; this garbage doesn't work
        """
        with shelve.open(os.path.join(MODULE_DIR, 'cache'), 'r') as db: # todo: refactor so that the cache is written below the base directory of the package, so that I can use relative file paths
            data = db['data']
            date = db['date']
        if check_date and (datetime.now().month in range(9, 12) and date.month in range(1, 7)):
            raise Exception(
                'It appears that the cache is from last school year. Please\n'
                'provide new data, re-instantiate, and re-write cache.'
            )
        return data

    @staticmethod
    def cache_exists():
        try:
            shelve.open(os.path.join(MODULE_DIR, 'cache'), 'r')
            return True
        except dbm.error:
            return False
