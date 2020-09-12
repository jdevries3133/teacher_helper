import os
import re
from time import sleep
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

from .exceptions import (
    InvalidViewError,
    CAException
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
        self.current_view = 'home'
        self.classrooms = {}
        # identify and assign as attribute the classrooms that are on the home page
        els = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div[2]/div/ol/li/div[1]/div[3]/h2/a[1]')))
        els = self.driver.find_elements(By.XPATH, '/html/body/div[2]/div/div[2]/div/ol/li/div[1]/div[3]/h2/a[1]')
        for el in els:
            self.classrooms.setdefault(el.text, el.get_attribute('href'))

    def navigate_to(self, view, *args, **kwargs):
        """
        Navigate to a particular classroom view.
        """
        # only accept valid views
        self._validate_view(view, *args, **kwargs)
        if view == 'home':
            self.driver.get('https://classroom.google.com/')
            self.current_view = 'home'
        if view == 'classroom':
            self.driver.get(self.classrooms[kwargs['classroom_name']])
            self.current_view = 'classroom'
        if view == 'classwork':
            if self.current_view != 'classroom':
                self.navigate_to('classroom', classroom_name=kwargs['classroom_name'])
                self._open_classwork_tab()
                self.current_view = 'classwork'

    def _get_assignment_url(self, assignment_name):
        """
        Must be called when the current view is classwork or classroom.
        """
        if self.current_view != 'classwork':
            self.navigate_to('classwork')
        breakpoint()

    def _validate_view(self, view, *args, **kwargs):
        """
        Argument validation for self.navigate_to() method.
        """
        if view not in [
            'home',
            'classroom',
            'classwork'
        ]:
            raise InvalidViewError(
                f'{view} is not a valid view.'
            )
        if view == 'classroom' or self.current_view != 'classroom' and view == 'classwork':
            print('cond')
            try:
                name = kwargs['classroom_name']
            except KeyError:
                raise InvalidViewError(
                    'To navigate to a classroom view, classroom_name must be'
                    'passed as a keyword argument'
                )

    def _open_classwork_tab(self):
        if self.current_view != 'classroom':
            raise InvalidViewError(
                'Cannot open classwork tab from view other than classroom '
                'view.'
            )
        url_validation_regex = (
            re.compile(r'https://classroom.google.com/u/(\d)/(c|w|r)/(\w{16})')
        )
        mo = re.search(
            url_validation_regex,
            self.driver.current_url
        )
        self.driver.get(
            f'https://classroom.google.com/u/{mo[1]}/w/{mo[3]}'
        )