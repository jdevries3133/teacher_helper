"""
Script to generate mock data.
"""

import csv
from pathlib import Path
from itertools import cycle
from random import randint

from teacherHelper import Helper

with open(
    Path(Path(__file__).parent, 'mock_data', 'random_names.csv'),
    'r'
) as csvf:
    rd = csv.reader(csvf)
    names = [r for r in rd]


def make_students_csv() -> list:
    teachers = [
        ', '.join((n1[0], n2[1])) for n1, n2 in zip(names[:30], names[1:31])
    ]
    teacher_grade = {
        teacher : f'{randint(4, 6)}th Grade'
        for teacher in teachers
    }
    rows = []
    for teacher, name in zip(cycle(teachers), names):
        first, last = name
        # Each row is:
        # first, last, grade jevel, homeroom teacher, email, birthday
        rows.append((
            first,
            last,
            teacher_grade[teacher],
            teacher,
            str(hash(first + last))[1:] + '@empacad.org',
            f'{randint(1, 13)}/{randint(1,28)}/{randint(2005, 2010)}'
        ))
    return rows

def make_parents_csv(students_csv_data: list):
    """
    Need to take the student data to make random parents for those students.

    Each row has:
    - Guardian First Name
    - Guardian Last Name
    - Student First Name
    - Student Last Name
    - Primary Contact
    - Guardian Email Address 1
    - Guardian Mobile Phone
    - Guardian Phone
    - Guardian Work Phone
    - Comments
    - Allow Contact
    - Student Resides With
    - Relation to Student
    """
    parent_names = [
        (first[0], last[1]) for first, last in zip(cycle(names[50:]), names)
    ] * 2
    rows = []
    for parent_name, student_row in zip(
        parent_names,
        cycle(students_csv_data[5:])
    ):
        # fix any accidental duplicates
        while ' '.join(parent_name) in [' '.join(n) for n in names]:
            parent_name = (
                names[randint(0, len(names) - 1)][0],
                parent_name[1]
            )
        rows.append([
            *parent_name,                               # guardian full name
            student_row[0],                             # student first name
            student_row[1],                             # student last name
            'Y',                                        # is primary contact
            f'{str(hash(parent_name))[1:]}@gmail.com',  # email
            str(randint(9730000000, 9739999999)),       # mobile phone
            *[''] * 2,                                  # home & work phone
            str(hash(student_row)),                     # comments
            ['Y', 'N'][randint(0, 1)],                  # allow contact
            ['Y', 'N'][randint(0, 1)],                  # student resides with
            [
                'Mother',
                'Father',
                'Other',
                'Grandmother',
                'Grandfather'
            ][randint(0, 4)]                            # relation to student
        ])
    return rows

def make_zoom_reports(students_csv_data: list):
    """
    Need to take the student data to make those students attend random zooms.
    """
