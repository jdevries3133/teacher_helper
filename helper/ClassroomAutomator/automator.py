import os
from time import sleep
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import pyautogui as pg

from .exceptions import (
    InvalidViewError,
)


class ClassroomAutomator:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = webdriver.Firefox()
        self.driver.get('https://classroom.google.com/u/1/h')
        xpath = '//*[@id="identifierId"]'
        username_elem = self.driver.find_element_by_xpath(xpath)
        username_elem.clear()
        username_elem.send_keys(self.username)
        username_elem.send_keys(Keys.RETURN)
        sleep(2.1)
        xpath = (
            '/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/'
            'div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div[1]'
            '/div/div/div/div/div[1]/div/div[1]/input'
        )
        password_elem = self.driver.find_element_by_xpath(xpath)
        password_elem.clear()
        password_elem.send_keys(self.password)
        password_elem.send_keys(Keys.RETURN)
        try:
            WebDriverWait(self.driver, 20).until(
                lambda driver: 'https://classroom.google.com' in driver.current_url
            )
        except TimeoutException:
            input(
                'Complete two factor auth challenge, then press enter to '
                'continue.'
            )
            WebDriverWait(self.driver, 20).until(
                lambda driver: 'https://classroom.google.com' in driver.current_url
            )
        self.current_view = 'home'

    def enforce_view(func):
        """
        Requires the driver to be in a particular view before the function is
        called. If the driver is not in the passed in view, it will navigate
        to it with the self.navigate_to(view) function.
        """
        def wrapper(*args):
            breakpoint()
            if args[0].current_view != args[1]:
                args[0].navigate_to(args[1])
            func(args)
        return wrapper

    def navigate_to(self, view, *args, **kwargs):
        """
        Navigate to a particular classroom view.
        """
        # only accept valid views
        self._validate_view(view, *args, **kwargs)
        if view == 'home':
            self.driver.get('https://classroom.google.com/')
        if view == 'classroom':
            if self.current_view != 'home':
                self.navigate_to('home')
            class_name = kwargs['classroom_name']
            breakpoint()

    def _validate_view(self, view, *args, **kwargs):
        """
        Argument validation logic for self.navigate_to() method.
        """
        if view not in [
            'home',
            'classroom',
        ]:
            raise InvalidViewError(
                f'{view} is not a valid view.'
            )
        if view == 'classroom':
            try:
                name = kwargs['classroom_name']
            except KeyError:
                raise InvalidViewError(
                    'To navigate to a classroom view, classroom_name must be'
                    'passed as a keyword argument'
                )

    # @enforce_view('classroom')
    def _open_materials_tab(self):

        url_validation_regex = (
            re.compile(r'https://classroom.google.com/u/(\d)/(c|w|r)/(\w{16})')
        )
        mo = re.search(
            url_validation_regex,
            driver.current_url
        )
        self.user_url_pararm = mo[1]
        self.class_id = mo[3]
        self.driver.get(
            f'https://classroom.google.com/u/{self.user_url_param}/w/{self.class_id}'
        )


    @classmethod
    def map_class_id_to_class_name(cls, username, password):
        """
        For methods that access class ids, this instantiates the object with
        class ids mapped to the class's names.
        """
        pass
