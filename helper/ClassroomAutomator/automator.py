import os
import re
from time import sleep
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException
)

from .exceptions import (
    InvalidViewError,
    CAException,
    AssignmentNamingConflict
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
                lambda dr: 'https://classroom.google.com' in dr.current_url
            )
        except TimeoutException:
            input(
                'Complete two factor auth challenge, then press enter to '
                'continue.'
            )
        self.current_view = 'home'
        self.classrooms = {}
        # identify and assign as attribute the classrooms that are on the
        # home page
        homepage_anchor_tags_for_each_classroom = (
            '/html/body/div[2]/div/div[2]/div/ol/li/div[1]/div[3]/h2/a[1]'
        )
        els = WebDriverWait(
            self.driver, 10
        ).until(EC.presence_of_element_located(
                (By.XPATH, homepage_anchor_tags_for_each_classroom)
            ))
        els = self.driver.find_elements(
            By.XPATH, homepage_anchor_tags_for_each_classroom
        )
        for el in els:
            self.classrooms.setdefault(el.text, el.get_attribute('href'))

    def navigate_to(self, view: str, *args, **kwargs):
        """
        Navigate to a particular classroom view.
        """
        # only accept valid views
        self._validate_view(view, *args, **kwargs)
        if view == 'home':
            self.driver.get('https://classroom.google.com/')
            self.current_view = 'home'
        elif view == 'classroom':
            self.driver.get(self.classrooms[kwargs['classroom_name']])
            self.current_view = 'classroom'
        elif view == 'classwork':
            if self.current_view != 'classroom':
                self.navigate_to(
                    'classroom', 
                    classroom_name=kwargs['classroom_name']
                )
                self._open_classwork_tab()
                self.current_view = 'classwork'
        elif view == 'assignment':
            url = self._get_assignment_url(kwargs['assignment_name'])
            self.driver.get(url)
        elif view == 'assignment_feedback':
            url = self._get_assignment_url(kwargs['assignment_name'])
            parts = url.split('/')
            sep = parts.index('c')
            base = '/'.join(parts[:sep]) + '/'
            av_url = base + f'g/tg/{parts[sep+1]}/{parts[sep+3]}'
            self.driver.get(av_url)

    def _get_assignment_url(self, assignment_name):
        """
        Must be called when the current view is classwork or classroom. Can be
        accessed through self.navigate_to('assignment' assignment_name=name)
        """
        if self.current_view != 'classwork':
            self.navigate_to('classwork')
        spans_with_assignment_names = WebDriverWait(
            self.driver, 20
        ).until(
            EC.presence_of_all_elements_located(
                (
                    By.XPATH,
                    '/html/body/div[2]/div/main/div/div/div[4]/ol/li/div/div/'
                    'div/div/ol/li/div/div/div/div/div/span'
                )
            )
        )
        el = [
            e for e in spans_with_assignment_names if e.text == assignment_name
        ]
        if len(el) > 1:
            raise AssignmentNamingConflict(
                'Two assignments in this classroom have the same name.'
                'ClassroomAutomator cannot know which one should be selected.'
                f'The duplicated name is {assignment_name}'
            )
        span_with_assignment_name = el[0]
        span_with_assignment_name.click()
        # might need try/catch if it happens too fast; need to see what error is
        # first.
        link_anchor = span_with_assignment_name.find_element_by_xpath(
            './../../../../../div[2]/div[2]/div/a'
        )
        link = link_anchor.get_attribute('href')
        return link

    def _validate_view(self, view, *args, **kwargs):
        """
        Argument validation for self.navigate_to() method.
        """
        # LIST OF AVAILABLE VIEWS
        if view not in [
            'assignment',
            'assignment_feedback',
            'home',
            'classroom',
            'classwork'
        ]:
            raise InvalidViewError(
                f'{view} is not a valid view.'
            )
        # CLASSROOM AND CLASSWORK (same validation logic)
        elif view == 'classroom' or view == 'classwork':
            if 'classroom_name' not in kwargs:
                raise InvalidViewError(
                    'To navigate to a classroom or classowork view, '
                    'classroom_name must be passed as a keyword argument'
                )
        # ASSIGNMENT VIEW
        elif view == 'assignment' or view == 'assignment_feedback':
            if self.current_view not in [
                'classwork',
                'classroom',
            ]:
                raise InvalidViewError(
                    'Must navigate to classroom or classwork before navigating '
                    'to an assignment'
                )
            if 'assignment_name' not in kwargs:
                raise InvalidViewError(
                    'assignment_name must be provided as a keyword argument to '
                    'navigate_to() in order to navigate to a specific '
                    'assignment.'
                )
            if self.current_view == 'classroom':
                self.navigate_to('classwork')
        else:
            raise CAException(
                'Error in _validate_view(), validation not performed on view:\n'
                    + view
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