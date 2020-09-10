from abc import ABC, abstractmethod
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import pyautogui as pg

from .automator import ClassroomAutomator


class FeedbackAutomator(ClassroomAutomator, ABC):
    def __init__(self, username, password, assignment_name: str, classroom_names: list):
        super().__init__(username, password)
        self.assignment_name = assignment_name
        self.classroom_names = classroom_names

    def loop(self):
        for classroom in classroom_names:
            self.navigate_to('classroom', classroom_name=classroom)
            breakpoint()

    @abstractmethod
    def assess(self):
        pass