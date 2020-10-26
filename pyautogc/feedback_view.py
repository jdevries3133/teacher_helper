"""
Automate the tedium of giving feedback on google-doc based assignments on google
classroom (WAY too much clicking – no thank you).

Scroll down to class FeedbackAutomator for a sample implementation. To get
going easily, read through the docstrings there, subclass and overwrite
the comment_bank method for your own custom comments, and away you go with
my default configuration.

For deeper extensibility, subclass the abstract base. You can do a lot, but also
avoid writing a lot of annoying selenium code. You will have to define the
following abstract methods:
    - assess
    - comment_bank

Optionally, you may also overwrite the "grade" and "give_feedback" methods. See
documentation for those specific methods for details.

The lifecycle of these subclassable methods are:
    - self._get_context()   => self.context gains "name", "attachments", and "grade_divisor"
    - self.assess()         => self.context gains "grade"
    - self.grade()          => self.context gains "percentage_grade"; grade is entered into Google Classroom
    - self.give_feedback()  => self.context gains "feedback". Feedback is entered into the DOM
    - self._cleanup()       =>

"""


from abc import ABC, abstractmethod
from types import SimpleNamespace

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from .automator import ClassroomAutomator
from .exceptions import ClassroomNameException


class FeedbackViewUtils(ClassroomAutomator):
    """
    Utility functions that specifically apply to the Assignment Feedback View
    in Google Classroom. Currently, the abstraction is very leaky because this
    class was rather carelessly extracted from the FeedbackAutomator class
    below. Hence, the __init__ needs things that shouldn't be necessary to
    the functionality of the class, and many of the methods are dependent on
    these things when they don't necessarily need to be.

    All methods prefixed with _av_ support _assignment_view_setup method.
    All methods prefixed with _gc_ support _get_context
    """

    def __init__(self, username: str, password: str, assignment_name: str, classroom_names: list, **kwargs):
        super().__init__(username, password)
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

    def _input_feedback(self):
        'Actually put the feedback into google classroom'
        breakpoint()

    def _input_grade(self):
        'Actually put the grade into google classroom'
        breakpoint()

    # TODO: move all the xpaths out into a constants folder or file
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
            self.context.get('assignment_statuses').setdefault(
                name,
                status
            )

    def _av_sort_by_status(self):
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
        WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable(
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
                breakpoint()
                raise StopIteration
        self._next_student()
        return self.driver, SimpleNamespace(**self.context)

    @ abstractmethod
    def assess(self):
        """
        Must add {"grade": int} into self.context. Grade must be an integer that
        is less than self.context["grade_divisor"].

        Must add {"feedback": str} into self.context. If self.context.get('feedback')
        returns None, no feedback will be sent.
        """

    @ abstractmethod
    def comment_bank(self, comment_index):
        """
        Must return your custom comments by index. For convention, if your
        feedback correlates with grades (and they probably will), put the
        "worst" comment first, and the "best" comment last. That way, the scale
        of grading will align with the indices. For example, a student who gets
        a grade of 4 might also get the fourth item in the comment bank list.

        Note that you can use f-strings and grab many things from self.context
        to compose highly responsive comment banks:
            self.context.get('name') => current student's name
            self.context.get('status') => current student's assignment status
            self.context.get('grade') => current student's grade (integer of fractional numerator)
            self.context.get('percentage_grade') => current student's grade (percentage value)

        Here's an example comment bank just for clarity:

        def comment_bank(self, comment_index):
            comments = [
                f'I hope you do better next time, {self.context.get('name')}. '
                f'you only got a {self.context.get('grade')} out of '
                f'{self.context.get('grade_divisor')}.',

                f'Great job, {self.context.get('name')}, you\'re a star!
            ]
            return comments[comment_index]
        """

    def give_feedback(self):
        """
        Always call super().give_feedback() if you overwrite this method. If you
        want your feedback to go somewhere other than into google classroom;
        for example:
            - Send to the homeroom teacher
            - Send to a parent
            - Save all custom feedback to a condensed report
        ... those would be good reasons to overwrite this.
        """
        self._input_feedback()  # in FeedbackViewUtils

    def grade(self):
        """
        Always call super().grade() if you overwrite this method. If you want
        the grade to go somewhere other than into google classroom; for example:
            - Email to parents
            - Save to a spreadsheet on your local device
            - Send to an administrator
            - Append to a gradebook
        ... those would be a good reasons to subclass this.
        """
        self.assess()
        assert isinstance(self.context.get('grade'), int)
        assert self.context.get('grade') <= self.context.get('grade_divisor')
        self.context['percentage_grade'] = (
            self.context.get('grade') / self.context.get('grade_divisor')
        )
        self._input_grade()  # in FeedbackViewUtils

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
        # raise Exception(
        #     """
        #     Need more context. Should add the following:
        #         self.context['name'] => current student's name
        #             * can probably be sliced from all names and statuses by current_student index
        #         self.context['status'] => assignment status
        #             * can probably be sliced from all names and statuses by current_student index
        #         self.context['grade_divisor'] => for calculating percentage grades
        #         self.context['is_assignment_graded'] => bool

        #     """
        # )
        return self.context


class FeedbackAutomator(FeedbackAutomatorBase):
    """
    Sample implementation of the base class. Subclassing this and overwriting
    the comment_bank method is a great way to get up and running quickly.

    Docstrings here describe this implementation and how it would be used.
    Docstrings in the abstract methods above give more technical details to help
    you with your implementation.

    In this impmentation, the user enters a single number in the terminal to
    assign a grade and provide feedback. The number is directly translated to
    the "Grade" field of Google Classroom. Note that any floating point grades
    are floored. I don't think that Google Classroom allows you to input
    percentage values anyway.

    The feedback from the comment bank is provided in response to the grade.
    The script reads the grade divisor from the DOM and determines the
    percentage grade. Then, the feedback is provided based on the following
    percentage grade bands:
        < 90%   => comment_bank(0)
        80-90%  => comment_bank(1)
        70%-80% => comment_bank(2)
        > 70%   => comment_bank(3)
    """

    def assess(self):
        """
        This assess method just takes user input. A nice additional feature is
        that you can provide custom feedback by simply inputting something other
        than a number. In that case, it will pass your custom feedback to the
        student as a private message and after you give your custom input,
        it will prompt you for a grade separately.
        """
        grade = input(f'Input grade for {self.context.get("name")}:\n')
        try:
            # floating point grades are floored.
            grade = int(e := float(grade))
            if not e.is_integer():
                print(f'WARNING: Grade has been floored from {e} to {grade}')
        except ValueError:
            custom_feedback = grade
            print(f'Providing custom feedback {custom_feedback}')

    def comment_bank(self, comment_index):
        """
        The assess method converts the user-input from 1-based to 0-based index.
        It is easier for the user to input a 1-based input because the keys are
        right next to each other on the keyboard. This method shoud simply have
        an array of comments and return comments[comment_index].

        Note that all of the context available in the iter_assess block is
        available here too as self.context. So, self.context['name'] can be
        used to access the current student\'s name.
        """
        comments = [
            # 0 (grade is 90%-100%)
            f'Awesome work, {self.context["name"]}! Have a great day 😊'
            # 1 (grade is 80%-90%)
            f'Nice job {self.context["name"]}! Take a look at the notes I left '
            'on your google doc.',
            # 2 (grade is 70%-80%)
            f'{self.context["name"]}, take a look at the comments I\'ve left'
            'in your work. Feel free to reply to this comment if you have'
            'any questions!',
            # 3 (grade is below 70%)
            f'{self.context["name"]}, this assignment is missing or incomplete. '
            'Please take a closer look at this, and send me a private comment '
            'back if you have any questions.\n\nI look forward to seeing your '
            'best work next time!',
        ]
        return comments[comment_index]

    def give_feedback(self):
        """
        This is actually NOT an abstract method. You can leave it alone, and
        feedback will be sent via a private message in google classroom like you
        probably want. But, if you want to do something custom with feedback,
        this is a good entrypoint.

        If you do specify this method in a subclass, remember to call
        super().give_feedback() for the feedback to still be sent into the
        google classroom private message.

        In this example, I'm saving a log of all the feedback that I give in a
        text file. I can get the feedback from context, through
        self.context.get('feedback').
        """
        super().give_feedback()
        with open('feedback_log.txt', 'a') as txt:
            txt.write(
                self.context.get('name')
                + '\n'
                + self.context.get('feedback') if self.context.get('feedback') else 'No Feedback'
                + '\n\n'
            )

    def grade(self):
        """
        This is also not an abstract method. By default, it will just put the
        grade into context as self.context['grade']

        In this example, I create a csv of the grades.
        """
        super().grade()
        with open('grades.csv', 'a') as csvfile:
            data = [
                self.context.get('name'),
                str(self.context.get('grade'))
                + ' / '
                + str(self.context.get('grade_divisor')),
                str(self.context.get('percentage_grade'))
                + '%'
            ]
            csvfile.write(','.join(data))
