import csv
import unittest
from unittest.mock import patch
from pathlib import Path

from .make_mocks import (
    make_students_csv,
    make_parents_csv,
    random_class
)

with open(
    Path(Path(__file__).parent, 'random_names.csv'),
    'r'
) as csvf:
    rd = csv.reader(csvf)
    names = [r for r in rd]

# smaller sample for fast test
@ patch('teacherhelper.tests.make_mocks.names', names[:100])
class TestMakeMocks(unittest.TestCase):

    def test_make_students_csv(self):
        data = make_students_csv()

        assert data  # no empty list
        for row in data:
            # check that student names come from list of random names
            assert ' '.join(row[:2]) in [' '.join(i) for i in names]

            # check that none of the teachers are also students
            teacher_last, teacher_first = row[3].split(', ')
            assert ' '.join((teacher_first, teacher_last)) not in [
                ' '.join(i) for i in names
            ]

        # check that homerooms are all in the same grade
        groups_by_teacher = {}
        for row in data:
            groups_by_teacher.setdefault(row[3], set())
            groups_by_teacher[row[3]].add(row[2])
        for set_ in groups_by_teacher.values():
            assert len(set_) == 1


    def test_make_parents_csv(self):
        students = make_students_csv()
        parents = make_parents_csv(students)

        assert parents  # no empty list
        for row in parents:
            # every row has 13 items
            assert len(row) == 13
            # row is all strings
            for i in row:
                assert isinstance(i, str)
            # unpack parent name variables
            parent_first_nm, parent_last_nm, *_ = row
            parent_name = ' '.join((
                parent_first_nm,
                parent_last_nm
            ))
            # no parent shares a name with a student
            assert parent_name not in [' '.join(n) for n in names]
            # no parent shares a name with a teacher
            teachers = set([' '.join(r[3].split(', ')[::-1]) for r in students])
            assert parent_name not in teachers
        # two parents for each student
        assert len(parents) / 2 == len(students)

    def test_random_class(self):
        """
        Test that students from a random class are actually all in the same
        class and grade level.
        """
        students = make_students_csv()
        class_ = random_class(students)
        for strow in class_:
            assert strow[2] == class_[0][2]
            assert strow[3] == class_[0][3]
