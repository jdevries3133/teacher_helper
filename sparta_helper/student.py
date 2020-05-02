import genesis

from bs4 import BeautifulSoup

class Student:
    def __init__(self, context):
        """
        Context must include:
            first name
            last name
            student id
            homeroom
            grade level
        """
        self.first_name = context['first_name']
        self.last_name = context['last_name']
        self.name = self.first_name + ' ' + self.last_name
        self.student_id = context['student_id']
        self.homeroom = context['homeroom']
        self.grade_level = context['grade_level']

        if context['email']:
            self.email = email

    def get_email(self):
        """
        Make post request to login, save cookies, then rock and roll baby.
        """
        session = genesis.get_session()
        link = (
            'https://genesis.sparta.org/sparta/sis/view?module=studentdata'
            '&category=modifystudent&tab1=demographics&tab2=contacts2&acti'
            f'on=form&studentid={self.student_id}&mode=cards'
        )
        resp = session.get(link)
        soup = BeautifulSoup(resp.text, features='html.parser')
        atags = soup.find_all('a')
        self.email = [t.text for t in atags if '@students.sparta.org' in t.text][0]
        print(f'Got email {self.email}\nFor {self.name}')

        return self.email


