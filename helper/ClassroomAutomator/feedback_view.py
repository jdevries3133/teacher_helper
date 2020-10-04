from types import SimpleNamespace

# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from .automator import ClassroomAutomator
from .exceptions import ClassroomNameException


class FeedbackAutomator(ClassroomAutomator):
    """
    Iteratively assess all assignments of a given name (str) in given classrooms
    (list).

    All methods prefixed with _av_ support _assignment_view_setup method.

    All methods prefixed with _gc_ support _get_context
    method.
    """

    def __init__(
        self,
        username: str,
        password: str,
        assignment_name: str,
        classroom_names: list,
        **kwargs
    ):
        super().__init__(username, password)
        self.assignment_name = assignment_name
        self.classroom_names = classroom_names
        self.only_turned_in = kwargs.get('only_turned_in') or False
        self.context = {}
        self.next_button_xpath = (
            '/html/body/div[4]/c-wiz/c-wiz/main/div[1]/div[1]/div[2]/div[2]'
        )
        # validate classroom names with names found from the DOM
        for name in classroom_names:
            if name not in self.classrooms:
                raise ClassroomNameException(
                    f'{name} does not match one of your google classrooms.\n'
                    'these are your google classrooms, which this program read '
                    f'from the DOM:\n\n{self.classrooms.keys()}'
                )
        # iterator indicies
        self.current_classroom = 0
        self.current_student = -1

    def __iter__(self):
        self.navigate_to('classwork', classroom_name=self.classroom_names[0])
        self.navigate_to(
            'assignment_feedback',
            assignment_name=self.assignment_name
        )
        self._assignment_view_setup()
        self._get_context()
        return self

    def __next__(self):
        self.current_student += 1
        if self.current_student >= len(self.context.get('assignment_statuses')) - 1:
            self._next_classroom()
            if self.current_classroom >= len(self.classroom_names) - 1:
                raise StopIteration
        self._next_student()
        return self.driver, SimpleNamespace(**self.context)

    def _next_student(self):
        if self.current_student == -1:
            self._get_context()
            return
        assert self.current_student < len(self.context['assignment_statuses'])
        self.driver.find_element_by_xpath(
            '/html/body/div[4]/c-wiz/c-wiz/main/div[1]/div[1]/div[2]/div[2]'
        ).click()
        self._get_context()

    def _next_classroom(self):
        self.current_classroom += 1
        self.current_student = -1
        self.navigate_to(
            'classwork',
            classroom_name=self.classroom_names[self.current_classroom]
        )
        self.navigate_to(
            'assignment_feedback',
            assignment_name=self.assignment_name
        )
        self.context = {}
        self._assignment_view_setup()
        self._get_context()

    def _assignment_view_setup(self):
        """
        Called the first time the assignment view loads.
        """
        self._av_sort_by_status()
        self._av_get_all_students()

    def _get_context(self):
        """
        Called for each student.
        """
        self._gc_parse_attachments()
        return self.context
