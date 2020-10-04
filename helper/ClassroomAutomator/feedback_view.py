from types import SimpleNamespace

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from .automator import ClassroomAutomator
from .exceptions import ClassroomNameException


class FeedbackViewUtils(ClassroomAutomator):
    def __init__(self, username: str, password: str, assignment_name: str, classroom_names: list, **kwargs):
        super().__init__(username, password, **kwargs)
        self.assignment_name = assignment_name
        self.classroom_names = classroom_names
        self.only_turned_in = kwargs.get('only_turned_in') or False
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
        # initialize attributes assigned or mutated by class methods
        self.context = {}

    def _av_get_all_students(self):
        self.context['assignment_statuses'] = {}
        names_xpath = (
            '/html/body/div[4]/c-wiz/c-wiz/main/div[1]/div[1]/div[1]/div/div[1]'
            '/div[1]/div[*]/span/div/div[1]'
        )
        statuses_xpath = (
            '/html/body/div[4]/c-wiz/c-wiz/main/div[1]/div[1]/div[1]/div/div[1]'
            '/div[1]/div[*]/span/div/div[3]/div/div/span[1]'
        )
        statuses = [
            self._normalize_status(i.get_attribute('textContent'))
            for i
            in self.driver.find_elements_by_xpath(statuses_xpath)
        ]
        names = [
            el.get_attribute('textContent')
            for el
            in self.driver.find_elements_by_xpath(names_xpath)
        ]
        assert len(names) == len(statuses)
        for name, status in zip(names, statuses):
            if self.only_turned_in and status != 'turned in':
                continue
            print((name, status))
            self.context.get('assignment_statuses').setdefault(
                name,
                status
            )

    def _av_sort_by_status(self):
        print('ind')
        # open dropdown
        student_dropdown_xpath = (
            '/html/body/div[4]/c-wiz/c-wiz/main/div[1]/div[1]/div[1]/div'
        )
        WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable(
            (By.XPATH, student_dropdown_xpath)
        )).click()
        # sort by status
        status_xpath = (
            '/html/body/div[4]/c-wiz/c-wiz/main/div[1]/div[1]/div[1]/div/div[2]'
            '/div[1]/div[4]/div[3]/span[3]'
        )
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, status_xpath)
        )).click()
        # click on first student
        first_student = (
            '/html/body/div[4]/c-wiz/c-wiz/main/div[1]/div[1]/div[1]/div/div[2]'
            '/div[2]/div[1]'
        )
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(
            (By.XPATH, first_student)
        )).click()

    def _gc_parse_attachments(self):
        self.context['attachments'] = []
        common_parent = (
            '/html/body/div[4]/c-wiz/c-wiz/main/div[2]/div[2]/div[2]/div[1]/div'
            '/div[1]/div[2]/div/div[2]/div/div/div'
        )
        single_assignment_label = (
            '/html/body/div[4]/c-wiz/c-wiz/main/div[2]/div[2]/div[2]/div[1]/div'
            '/div[1]/div[2]/div/div[2]/div/div/div/span/div[2]/div/span[2]'
        )
        multiple_assignment_labels = (
            '/html/body/div[4]/c-wiz/c-wiz/main/div[2]/div[2]/div[2]/div[1]/div'
            '/div[1]/div[2]/div/div[2]/div/div/div/div/span/div/div/span[2]'
        )
        # wait for parent element to mount
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, common_parent))
        )
        try:
            label_el = self.driver.find_element_by_xpath(
                single_assignment_label
            )
            if 'Veerendrasakthi Prabhurajan' in label_el.text:
                print('bp')
            self.context['attachments'].append({
                'name': label_el.text,
                'label_xpath': single_assignment_label,
                'href': 'not yet implemented in _gc_parse_attachments()'
            })
        except NoSuchElementException:
            label_els = self.driver.find_elements_by_xpath(
                multiple_assignment_labels
            )
            for i, el in enumerate(label_els):
                xpath = (
                    '/html/body/div[4]/c-wiz/c-wiz/main/div[2]/div[2]/div[2]/di'
                    f'v[1]/div/div[1]/div[2]/div/div[2]/div/div[{i}]/div/div/sp'
                    f'an/div[{i}]/div/span[2]'
                )
                self.context['attachments'].append({
                    'name': el.text,
                    'label_xpath': xpath,
                    'href': 'not yet implemented in _gc_parse_attachments()'
                })

    @ staticmethod
    def _normalize_status(status):
        for normalized in [
            'returned',
            'missing',
            'turned in',
            'assigned'
        ]:
            if normalized in status.lower():
                return normalized
        raise Exception(f'Invalid status: {status}')


class FeedbackAutomatorBase(FeedbackViewUtils, ABC):
    """
    Iteratively assess all assignments of a given name (str) in given classrooms
    (list).

    All methods prefixed with _av_ support _assignment_view_setup method.

    All methods prefixed with _gc_ support _get_context
    method.
    """

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
