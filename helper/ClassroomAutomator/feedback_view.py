from abc import ABC, abstractmethod
from types import SimpleNamespace

# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
# from selenium.webdriver.common.keys import Keys
# from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

from .automator import ClassroomAutomator
from .exceptions import ClassroomNameException


class FeedbackAutomator(ClassroomAutomator):
    def __init__(self, username, password, assignment_name: str, classroom_names: list):
        super().__init__(username, password)
        self.assignment_name = assignment_name
        self.classroom_names = classroom_names
        self.current_classroom = classroom_names[0]
        self.assignment_view_context = {}
        # validate classroom names with names found from the DOM
        for name in classroom_names:
            if name not in self.classrooms:
                raise ClassroomNameException(
                    f'{name} does not match one of the following classroom '
                    f'names read from the DOM:\n\n{self.classrooms.keys()}'
                )

    def iter_assess(self):
        for classroom in self.classroom_names:
            self.navigate_to('classwork', classroom_name=classroom)
            self.navigate_to('assignment_feedback',
                             assignment_name=self.assignment_name)
            # loop through all students
            for student in ['all_students']:
                self._get_assignment_view_context()
                yield self.driver, SimpleNamespace(**self.assignment_view_context)

    def _get_assignment_view_context(self):
        self.assignment_view_context = {
            'attachments': []
        }
        # need to figure out if there is one or multiple drive attachments
        common_parent = '/html/body/div[4]/c-wiz/c-wiz/main/div[2]/div[2]/div[2]/div[1]/div/div[1]/div[2]/div/div[2]/div/div/div'
        single_assignment_label = '/html/body/div[4]/c-wiz/c-wiz/main/div[2]/div[2]/div[2]/div[1]/div/div[1]/div[2]/div/div[2]/div/div/div/span/div[2]/div/span[2]'
        multiple_assignment_labels = '/html/body/div[4]/c-wiz/c-wiz/main/div[2]/div[2]/div[2]/div[1]/div/div[1]/div[2]/div/div[2]/div/div/div/div/span/div/div/span[2]'
        parent = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, common_parent))
        )
        try:
            label_el = self.driver.find_element_by_xpath(
                single_assignment_label
            )
            self.assignment_view_context['has_multiple_attachments'] = False
            self.assignment_view_context['attachment_name'] = label_el.text
            self.assignment_view_context['attachments'].append(
                {'name': label_el.text, 'xpath': single_assignment_label})
        except NoSuchElementException:
            label_els = self.driver.find_elements_by_xpath(
                multiple_assignment_labels
            )
            self.assignment_view_context['has_multiple_attachments'] = True
            for el in label_els:
                print('navigate to click element')
                breakpoint()
        all_names = '/html/body/div[4]/c-wiz/c-wiz/main/div[1]/div[1]/div[1]/div/div[1]/div[1]/div/span/div/div[1]'
        name_els = self.driver.find_elements_by_xpath(all_names)
        for el in name_els:
            if el.get_attribute('visibility') != 'hidden':
                pass

