from abc import ABC, abstractmethod
import re

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.keys import Keys
# from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
# import pyautogui as pg

from .automator import ClassroomAutomator
from .exceptions import ClassroomNameException


class FeedbackAutomator(ClassroomAutomator, ABC):
    def __init__(self, username, password, assignment_name: str, classroom_names: list):
        super().__init__(username, password)
        self.assignment_name = assignment_name
        self.classroom_names = classroom_names
        # validate classroom names with names found from the DOM
        for name in classroom_names:
            if name not in self.classrooms:
                raise ClassroomNameException(
                    f'{name} does not match one of the following classroom '
                    f'names read from the DOM:\n\n{self.classrooms.keys()}'
                )

    def loop(self):
        for classroom in self.classroom_names:
            self.navigate_to('classwork', classroom_name=classroom)
            self.navigate_to('assignment_feedback',
                             assignment_name=self.assignment_name)
            self.download_document_as('word_doc')
            breakpoint()

    @abstractmethod
    def assess(self):
        pass
