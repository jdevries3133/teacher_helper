import csv
import os

from bs4 import BeautifulSoup

from .genesis import get_session

class Student:
    def __init__(self, context):
        """
        Context must include:
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

    def get_genesis_email(self):
        """
        Make post request to login, save cookies, then rock and roll baby.
        """
        try:
            session = get_session()
            link = (
                'https://genesis.sparta.org/sparta/sis/view?module=studentdata'
                '&category=modifystudent&tab1=demographics&tab2=contacts2&acti'
                f'on=form&studentid={self.student_id}&mode=cards'
            )
            resp = session.get(link)
            soup = BeautifulSoup(resp.text, features='html.parser')
            atags = soup.find_all('a')
            breakpoint()
            self.email = [t.text for t in atags if '@students.sparta.org' in t.text][0].lower()
            print(f'Got email {self.email}\nFor {self.name}')

            return self.email

        except Exception as e:
            return f'failed on {self.name} due to exception: {e}'

    def get_email_from_csv(self, direc=None):
        if 'student_emails.csv' not in os.listdir('.'):
            raise Exception(
                '"student_emails.csv" must be present in the module directory, '
                'or its path must be passed to to this function as an optional '
                'parameter.'
            )
            if not direc:
                direc = 'student_emails.csv'

            with open(direc, 'r') as csvfile:
                rd = csv.reader(csvfile)
                my_row = [r for r in rd if r[0] == self.student_id]
                print('finish writing this function boi')
                breakpoint()
                self.email = my_row[1]
