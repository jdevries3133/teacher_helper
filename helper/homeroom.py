import csv
from datetime import datetime
import os
import re
import shelve

from .meta_groups import MetaGroup
from .student import Student

class Homeroom(MetaGroup):
    def __init__(self, teacher, grade_level, students):
        """
        Ensure that string constants for csv headers of id, student names, and
        (if applicable) student emails are correct.
        """
        self.teacher = teacher
        self.grade_level = grade_level
        self.students = students
