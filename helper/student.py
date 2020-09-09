import csv
import os

class Student:
    def __init__(self, context):
        """
        Context may include:
            first_name
            last_name
            student_id
            homeroom
            grade_level
        """
        need_defaults = [
            'first_name',
            'last_name',
            'student_id',
            'homeroom',
            'grade_level',
            'groups',
            'email',
            'guardians'
        ]
        context.setdefault('groups', [])
        context.setdefault('guardians', [])
        for key in need_defaults:
            context.setdefault(key, None)
            self.__setattr__(key, context[key])
        self.name = self.first_name + ' ' + self.last_name
