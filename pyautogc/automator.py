from time import sleep
import re

from selenium.common.exceptions import (
    TimeoutException,
)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver

from .exceptions import (
    InvalidViewError,
    CAException,
    AssignmentNamingConflict
)
from .xpaths import Xpaths


class ClassroomAutomator:
    def __init__(self, username: str, password: str):
        assert isinstance(username, str)
        assert isinstance(password, str)
        self.username = username
        self.password = password
        self.driver = webdriver.Firefox()
        self.driver.get('https://classroom.google.com/u/1/h')
        username_elem = self.driver.find_element_by_xpath(
            Xpaths.login_username
        )
        username_elem.clear()
        username_elem.send_keys(self.username)
        username_elem.send_keys(Keys.RETURN)
        sleep(2.1)
        password_elem = self.driver.find_element_by_xpath(
            Xpaths.login_password
        )
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
        els = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH, 
                    Xpaths.homepage_anchor_tags_for_each_classroom
                )
            )
        )
        els = self.driver.find_elements(
            By.XPATH, Xpaths.homepage_anchor_tags_for_each_classroom
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
            # TODO split into separate function
            parts = url.split('/')
            sep = parts.index('c')
            base = '/'.join(parts[:sep]) + '/'
            av_url = base + f'g/tg/{parts[sep+1]}/{parts[sep+3]}'
            self.driver.get(av_url)
        else:
            raise Exception(f'Invalid view: {view}')

    def download_document_as(self, download_type):
        """
        Download the current document in a given file format.
        """
        if self.current_view != 'assignment_feedback':
            raise InvalidViewError(
                'Document must be downloaded from assignment feedback view'
            )
        download_queries = {
            'word_doc': 'Download as Microsoft Word',
            'pdf': 'Download as PDF Document',
            'html': 'Download as Web Page',
            'plain_text': 'Download as Plain Text',
        }
        if download_type not in download_queries:
            raise CAException(
                f'{download_type} is not a valid download type'
            )
        inp = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    Xpaths.fb_menu_bar_text_search
                )
            )
        )
        inp.send_keys(download_queries[download_type] + u'\ue007')
        inp.clear()
        raise NotImplementedError('jack: Not yet implemented.')

    def _get_assignment_url(self, assignment_name, raise_exception=False):
        """
        Must be called when the current view is classwork or classroom. Can be
        accessed through self.navigate_to('assignment' assignment_name=name)
        """
        if self.current_view != 'classroom' and self.current_view != 'classwork':
            raise Exception(
                'Must be called when the current view is classwork or classroom'
            )
        if self.current_view != 'classwork':
            self.navigate_to('classwork')
        spans_with_assignment_names = WebDriverWait(self.driver, 40).until(
            EC.presence_of_all_elements_located(
                (
                    By.XPATH,
                    Xpaths.cw_all_assignment_names
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
        try:
            span_with_assignment_name = el[0]
        except IndexError:
            if raise_exception:
                raise CAException(
                    f'Assignment "{assignment_name}" was not found'
                )
            name = input(
                f'{assignment_name} was not found in the '
                'google classroom. Press enter to try again.\n\nIf '
                f'{assignment_name} is incorrect, enter the correct name and '
                'press enter.'
            ).strip()
            if name:
                self._get_assignment_url(name)
            else:
                sleep(2)
                return self._get_assignment_url(assignment_name, raise_exception=True)
        span_with_assignment_name.click()
        # might need try/catch if it happens too fast; need to see what error is
        # first.
        link_anchor = span_with_assignment_name.find_element_by_xpath(
            Xpaths.cw_anchor_tag_relative_to_assignment_name_span 
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
        if view in ['classroom', 'classwork']:
            if 'classroom_name' not in kwargs:
                raise InvalidViewError(
                    'To navigate to a classroom or classowork view, '
                    'classroom_name must be passed as a keyword argument'
                )
        # ASSIGNMENT VIEW
        if view in ['assignment', 'assignment_feedback']:
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
                self.navigate_to(
                    'classwork', classroom_name=kwargs.get('classroom_name'))
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
