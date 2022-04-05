import csv
from pathlib import Path

from .fixtures import students_csv, parents_csv

with open(Path(Path(__file__).parent, "random_names.csv"), "r") as csvf:
    rd = csv.reader(csvf)
    names = [r for r in rd]


def test_make_students_csv(students_csv):
    # data after the header row
    data = students_csv[1:]

    assert data  # no empty list
    for row in data:
        # check that student names come from list of random names
        assert " ".join(row[:2]) in [" ".join(i) for i in names]

        # check that none of the teachers are also students
        teacher_last, teacher_first = row[3].split(", ")
        assert " ".join((teacher_first, teacher_last)) not in [
            " ".join(i) for i in names
        ]

    # check that homerooms are all in the same grade
    groups_by_teacher = {}
    for row in data:
        groups_by_teacher.setdefault(row[3], set())
        groups_by_teacher[row[3]].add(row[2])
    for set_ in groups_by_teacher.values():
        assert len(set_) == 1


def test_make_parents_csv(students_csv, parents_csv):
    students = students_csv[1:]
    parents = parents_csv[1:]

    assert parents  # no empty list
    for row in parents:
        # every row has 13 items
        assert len(row) == 13
        # row is all strings
        for i in row:
            assert isinstance(i, str)
        # unpack parent name variables
        parent_first_nm, parent_last_nm, *_ = row
        parent_name = " ".join((parent_first_nm, parent_last_nm))
        # no parent shares a name with a student
        assert parent_name not in [f"{s[0]} {s[1]}" for s in students]
        # no parent shares a name with a teacher
        teachers = set([" ".join(r[3].split(", ")[::-1]) for r in students])
        assert parent_name not in teachers
    # roughly two parents for each student
    assert -2 < len(parents) // 2 - len(students) < 2
