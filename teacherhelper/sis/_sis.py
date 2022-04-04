import os
import dbm
import shelve
from typing import Union, cast, Dict
from datetime import datetime

from fuzzywuzzy import process

from .._data_dir import get_data_dir
from ._entities import Group, Homeroom, ParentGuardian, Student
from ._oncourse_mixin import OnCourseMixin


class Sis(OnCourseMixin):
    """Student information system."""

    def __init__(
        self,
        homerooms: Dict[str, Homeroom],
        students: Dict[str, Student],
        groups: Dict[str, Group],
    ):
        self.homerooms = homerooms
        self.students = students
        self.groups = groups
        self.cache_dir = os.path.join(__file__, "cache")

    def write_cache(self):
        with shelve.open(os.path.join(get_data_dir(), "cache"), "c") as db:
            db["data"] = self
            db["date"] = datetime.now()

    def find_student(
        self, student_name: str, threshold: int = 90
    ) -> Union[Student, None]:
        """Returns a student object. If auto_yes=True, it will presume that the
        best matching student is correct. Optionally, set a levenshtien distance
        threshold below which students will not be included."""
        if not isinstance(student_name, str):
            raise Exception("Student name must be a string")

        # direct match
        if st := self.students.get(student_name.title()):
            return st

        # get nearest match
        if result := process.extractOne(student_name, self.students.keys()):
            closest_name, confidence = result[0], result[1]
            if confidence >= threshold:
                return self.students[closest_name]

    def find_parent(
        self, parent_name: str, threshold: int = 70
    ) -> Union[ParentGuardian, None]:
        """Return a parent matching the given name, preferentially searching
        amongst primary contacts. May return `None` if there is not a close
        match."""
        # build mapping of parent name to string so we can perform a fuzzy
        # search. Make separate collections of all_guardians and
        # primary_guardians so we can prefer to match primaries
        all_guardians = {}
        primary_guardians = {}
        for st in self.students.values():
            for g in st.guardians:
                all_guardians.setdefault(g.name, g)
                if g.primary_contact:
                    primary_guardians.setdefault(g.name, g)
            primary_contact = cast(ParentGuardian, st.primary_contact)
            if primary_contact is not None:
                primary_guardians.setdefault(primary_contact.name, primary_contact)
            # insert the other guardians only if there is no primary
            else:
                for g in st.guardians:
                    all_guardians.setdefault(g.name, g)

        # prefer match amongst primary contacts
        primary_match = process.extractOne(
            parent_name, [g.name for g in primary_guardians.values()]
        )
        if primary_match and primary_match[1] > threshold:
            if mo := primary_guardians.get(primary_match[0]):
                return mo

        # search all parents and guardians otherwise
        name_match = process.extractOne(
            parent_name, [g.name for g in all_guardians.values()]
        )
        if (
            name_match
            and name_match[1] > threshold
            and (mo := all_guardians.get(name_match[0]))
        ):
            return mo

    @classmethod
    def read_cache(cls, check_date=True):
        """Return the pickled Sis instance from $HELPER_DATA/cache"""
        if not cls.cache_exists():
            raise IOError("cache does not exist")
        with shelve.open(os.path.join(get_data_dir(), "cache"), "r") as db:
            cls = cast(cls, db["data"])
            date: datetime = cast(datetime, db["date"])

        if check_date and (
            datetime.now().month in range(9, 12) and date.month in range(1, 7)
        ):
            raise ValueError("cache is out of date")
        return cls

    @staticmethod
    def cache_exists():
        """Check for existence of the cache at $HELPER_DATA/cache"""
        try:
            sh = shelve.open(os.path.join(get_data_dir(), "cache"), "r")
            sh.close()
            return True
        except dbm.error:
            return False
