"""
Script to generate mock data.
"""

import csv
from pathlib import Path
from itertools import cycle
from typing import List
import random

import pytest


with open(Path(Path(__file__).parent, "random_names.csv"), "r") as csvf:
    rd = csv.reader(csvf)
    names = [r for r in rd]


@pytest.fixture
def students_csv() -> list:
    teachers = [", ".join((n1[0], n2[1])) for n1, n2 in zip(names[:30], names[1:31])]
    teacher_grade = {teacher: f"{random.randint(4, 7)}th Grade" for teacher in teachers}
    rows = [
        [
            "First Name",
            "Last Name",
            "Grade Level",
            "Homeroom Teacher",
            "Email Address 1",
            "Birth Date",
        ]
    ]
    for teacher, name in zip(cycle(teachers), names[:300]):
        first, last = name
        # Each row is:
        # first, last, grade level, homeroom teacher, email, birthday
        rows.append(
            [
                first,
                last,
                teacher_grade[teacher],
                teacher,
                str(hash(first + last))[1:] + "@empacad.org",
                # birthday
                f"{random.randint(1, 13)}/{random.randint(1,28)}/{random.randint(2005, 2010)}",
            ]
        )
    return rows


@pytest.fixture
def parents_csv(students_csv):
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
    students_csv_data = students_csv[1:]  # skip header row
    parent_names = names[300:900]
    rows = [
        [
            "Guardian First Name",
            "Guardian Last Name",
            "Student First Name",
            "Student Last Name",
            "Primary Contact",
            "Guardian Email Address 1",
            "Guardian Mobile Phone",
            "Guardian Phone",
            "Guardian Work Phone",
            "Comments",
            "Allow Contact",
            "Student Resides With",
            "Relation to Student",
        ]
    ]
    for parent_name, student_row in zip(parent_names, cycle(students_csv_data)):
        rows.append(
            [
                *parent_name,  # guardian full name
                student_row[0],  # student first name
                student_row[1],  # student last name
                "Y",  # is primary contact
                f"{str(hash(''.join(parent_name)))[1:]}@gmail.com",  # email
                str(random.randint(9730000000, 9739999999)),  # mobile phone
                *[""] * 2,  # home & work phone
                str(hash(tuple(student_row))),  # comments
                ["Y", "N"][random.randint(0, 1)],  # allow contact
                ["Y", "N"][random.randint(0, 1)],  # student resides with
                ["Mother", "Father", "Other", "Grandmother", "Grandfather"][
                    random.randint(0, 4)
                ],  # relation to student
            ]
        )
    return rows
