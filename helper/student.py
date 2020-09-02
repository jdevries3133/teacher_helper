import csv
import os

from bs4 import BeautifulSoup

from .genesis import get_session

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
            'email'
        ]
        context.setdefault('groups', [])
        for key in need_defaults:
            context.setdefault(key, None)
        self.first_name = context['first_name']
        self.last_name = context['last_name']
        self.name = self.first_name + ' ' + self.last_name
        self.student_id = context['student_id']
        self.homeroom = context['homeroom']
        self.grade_level = context['grade_level']
        self.groups = context['groups']
        self.email = context['email']
