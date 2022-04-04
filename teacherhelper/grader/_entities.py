from dataclasses import dataclass
from typing import Dict, Literal, Union

from teacherhelper.sis import Student


@dataclass
class Config:
    """Config can be defined as a yaml file in the root of the project named
    `overrides.yml`. It is loaded by `__main__.load_config`"""

    # where key is student name and value is the comment
    notes: Dict[str, str]

    # top-level key is a student name. top-level value is a dict of grade type
    # to override value. The override dict can be partially complete.
    grade_overrides: Dict[
        str, Dict[Literal["week 19", "week 20", "week 21", "total"], int]
    ]

    # where key is student name and value is the overriden grade level
    grade_level_override: Dict[str, int]


@dataclass
class GradeResult:
    student: Student
    assignment: str
    grade: int


@dataclass
class Page:
    student: Student
    wk_19_grade: int
    wk_20_grade: int
    wk_21_grade: int

    notes: Union[str, None] = None

    total_grade_override: Union[int, None] = None

    @property
    def total_grade(self):
        if self.total_grade_override:
            return self.total_grade_override

        # `other_stuff` are the things in the rubric whose value is fixed. This
        # is different for fifth grade, because they have music fewer times
        # each week.
        other_stuff = 20 if self.student.grade_level == 5 else 40
        return other_stuff + self.wk_19_grade + self.wk_20_grade + self.wk_21_grade
