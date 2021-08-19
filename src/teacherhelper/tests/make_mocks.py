"""
Script to generate mock data.
"""

import csv
from pathlib import Path
from itertools import cycle
from typing import List
import random


with open(Path(Path(__file__).parent, 'random_names.csv'), 'r') as csvf:
    rd = csv.reader(csvf)
    names = [r for r in rd]


def make_students_csv() -> list:
    teachers = [
        ', '.join((n1[0], n2[1])) for n1, n2 in zip(names[:30], names[1:31])
    ]
    teacher_grade = {
        teacher : f'{random.randint(4, 6)}th Grade'
        for teacher in teachers
    }
    rows = []
    for teacher, name in zip(cycle(teachers), names):
        first, last = name
        # Each row is:
        # first, last, grade level, homeroom teacher, email, birthday
        rows.append((
            first,
            last,
            teacher_grade[teacher],
            teacher,
            str(hash(first + last))[1:] + '@empacad.org',
            f'{random.randint(1, 13)}/{random.randint(1,28)}/{random.randint(2005, 2010)}'
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
                names[random.randint(0, len(names) - 1)][0],
                parent_name[1]
            )
        rows.append([
            *parent_name,                               # guardian full name
            student_row[0],                             # student first name
            student_row[1],                             # student last name
            'Y',                                        # is primary contact
            f'{str(hash(parent_name))[1:]}@gmail.com',  # email
            str(random.randint(9730000000, 9739999999)),       # mobile phone
            *[''] * 2,                                  # home & work phone
            str(hash(student_row)),                     # comments
            ['Y', 'N'][random.randint(0, 1)],                  # allow contact
            ['Y', 'N'][random.randint(0, 1)],                  # student resides with
            [
                'Mother',
                'Father',
                'Other',
                'Grandmother',
                'Grandfather'
            ][random.randint(0, 4)]                            # relation to student
        ])
    return rows

def random_class(students_csv_data: list) -> List[str]:
    teacher = random.sample(students_csv_data, 1)[0][3]
    return [s for s in students_csv_data if s[3] == teacher]


