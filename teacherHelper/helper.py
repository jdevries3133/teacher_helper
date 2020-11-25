import os
import logging
import dbm
import shelve
from datetime import datetime

from fuzzywuzzy import process

from .HelperMixins import OnCourseMixin, SillyMixin

MODULE_DIR = os.path.dirname(__file__)
logger = logging.getLogger(__name__)


class Helper(OnCourseMixin, SillyMixin):
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
        if not isinstance(student_name, str):
            raise Exception("Student name must be a string")
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
            logger.debug(f'Exact match for {st.name}')
            return st

        # get nearest match
        closest_name, confidence = process.extractOne(
            student_name,
            self.students.keys()
        )

        logger.debug(
            f'{closest_name} is similar to {student_name} with a confidence of '
            + str(confidence)
        )
        if auto_yes:
            match = True
        else:
            match = self.match_in_terminal(student_name, closest_name)
        if match and not auto_yes:
            # allow match to pass regardless of thmatchhold if match was provided
            # by user input
            return self.students[closest_name]
        if match and auto_yes:
            if confidence > threshold:
                logger.debug(
                    f'Fuzzy match; {student_name} == {closest_name}::'
                    f'confidence = {confidence}::threshold = {threshold}'
                )
                return self.students[closest_name]
            logger.debug('Match rejected; confidence too low')
        if not auto_yes:  # provide feedback to user
            print('Student object not found. find_nearest_match will return None')
        # None will be returned if no return conditions are met

    def exhaustive_search(self, name, subgroup=None, threshold=70):
        """
        Split the name into words and check if each word is a unique first or
        last name within the subgroup. If calling this function frequently
        on repeated datasets, try to cache the results because this function
        is slow.
        """
        # try matching normally first with default threshold of 90
        st = self.find_nearest_match(name, auto_yes=True)
        if st:
            logger.debug(f'Basic search for {name} returned {st.name}')
            return st
        logger.debug(f'Basic search for {name} returned None')
        if (st := self.search_within_subgroup(name,
                                              subgroup,
                                              threshold=threshold)):
            return st
        logger.debug(f'Full name subgroup search for {name} returned None')

        if not ' ' in name:
            name_parts = [name]
        else:
            name_parts = ' '.split(name)

        logger.debug(f'Searching through words {name_parts}')

        # search each name part as each role
        for np in name_parts:
            for type_ in ['last_name', 'first_name']:
                if (st := self.search_within_subgroup(np,
                                                      subgroup,
                                                      name_part=type_,
                                                      threshold=threshold)):
                    logger.debug(f'{name} matched with {st.name} by {type_}')
                    return st
            logger.debug(f'{type_} subgroup search for {name} returned None')

    def search_within_subgroup(self, name, subgroup: list, threshold=90, name_part='name'):
        """
        subgroup should be a list of Student objects to search within. threshold
        is the confidence threshold. name_part is the part of the name that
        "name" is declared to be. Can be 'first_name', 'last_name', or just
        'name' (full name). At a higher level, this allows more or less
        exhaustive searching by calling this function multiple times.
        """
        logger.debug(f'Checking {name} as a {name_part}')
        name_match = process.extract(
            name,
            [getattr(s, name_part) for s in subgroup],
            limit=2
        )

        # Check whether name is unique within subgroup.
        if name_match[1][0] == name_match[0][0]:
            logger.debug(
                f'Cannot proceed with {name}. More than one '
                f'student in the subgroup has the first '
                f'name {name_match[0][0]}.'
            )

        # check for confidence
        if name_match[0][1] < threshold:
            logger.debug(
                f'{name_match[0][0]} rejected against {name} because the '
                f'confidence of {name_match[0][1]} was below the threshold of '
                + str(threshold)
            )
            return  # does not pass threshold

        name = name_match[0][0]

        if name == 'name':  # shortcut for full name matches
            if (st := self.students[name]):
                logger.debug('Hit on full name match shortcut')
                return st

        # we know the name is unique in the subgroup, so find the corresponding
        # Student object in the subgroup and return it.
        for st in self.students.values():

            if not st in subgroup:
                continue

            # break when we find the right student
            if name in st.name:
                break

        logger.debug(
            f'SUBGROUP MATCH {name} matches with {st.name} within subgroup.'
        )

        return st

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
