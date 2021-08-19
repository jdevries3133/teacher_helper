import os
from pathlib import Path
import logging
import dbm
import shelve
from typing import Union
from datetime import datetime

from fuzzywuzzy import process

from .entities import Student
from .oncourse_mixin import OnCourseMixin


logger = logging.getLogger(__name__)


class HelperError(Exception): ...
class CacheError(HelperError): ...


class Helper(OnCourseMixin):
    """
    Driver for the entire module! See README.md test
    """

    DATA_DIR = (os.getenv('HELPER_DATA')
                or Path(Path(__file__).parents[1], 'private'))

    def __init__(self, homerooms: dict, students: dict, groups: dict):
        self.homerooms = homerooms
        self.students = students
        self.groups = groups
        self.cache_dir = os.path.join(__file__, 'cache')

    def write_cache(self):
        with shelve.open(os.path.join(self.DATA_DIR, 'cache'), 'c') as db:
            db['data'] = self
            db['date'] = datetime.now()

    def find_nearest_match(self, student_name: str, threshold=90, **_) -> Union[Student, None]:
        """
        Returns a student object. If auto_yes=True, it will presume that the
        best matching student is correct. Optionally, set a levenshtien distance
        threshold below which students will not be included.
        """
        if not isinstance(student_name, str):
            raise Exception("Student name must be a string")

        # direct match
        if st := self.students.get(student_name.title()):
            logger.debug(f'Exact match for {st.name}')
            return st

        # get nearest match
        if result := process.extractOne(
                student_name,
                self.students.keys()
        ):
            closest_name, confidence = result[0], result[1]
            if confidence >= threshold:
                return self.students[closest_name]

    def find_parent(self, parent_name):
        # create dict of guardians & primary_contacts
        all_guardians = {}
        primary_contacts = {}
        for st in self.students.values():
            try:
                primary = st.primary_contact
                primary_contacts.setdefault(primary.name, primary)
            except AttributeError:
                pass
            for g in st.guardians:
                all_guardians.setdefault(g.name, g)

        # prefer match amongst primary contacts
        primary_match = process.extractOne(
            parent_name,
            [g.name for g in primary_contacts.values()]
        )
        if primary_match and primary_match[1] > 85:
            if mo :=  primary_contacts.get(primary_match[0]):
                return mo.student

        # search all parents and guardians otherwise
        name_match = process.extractOne(
            parent_name,
            [g.name for g in all_guardians.values()]
        )
        if name_match and (mo := all_guardians.get(name_match[0])):
            return mo.student

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
            for role in ('last_name', 'first_name'):
                if (st := self.search_within_subgroup(np,
                                                      subgroup,
                                                      name_part=role,
                                                      threshold=threshold)):
                    logger.debug(f'{name} matched with {st.name} by {role}')
                    return st
        logger.debug(f'Exhaustive search for {name} failed')

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
        # TODO: refactor
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

    @ classmethod
    def read_cache(cls, check_date=True):
        """
        This static method returns a class because I like to break the rules.
        there's a reason for the rules; this garbage doesn't work
        """
        with shelve.open(os.path.join(cls.DATA_DIR, 'cache'), 'r') as db:
            cls = db['data']
            date = db['date']
        if check_date and (datetime.now().month in range(9, 12) and date.month in range(1, 7)):
            raise Exception(
                'It appears that the cache is from last school year. Please\n'
                'provide new data, re-instantiate, and re-write cache.'
            )
        return cls

    @ staticmethod
    def cache_exists():
        try:
            sh = shelve.open(os.path.join(Helper.DATA_DIR, 'cache'), 'r')
            sh.close()
            return True
        except dbm.error:  # type: ignore
            return False

