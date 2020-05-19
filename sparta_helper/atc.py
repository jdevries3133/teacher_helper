"""
Because both the homeroom and groups should have an add to classroom function,
and I am starting to regret not making an abstract base class.
"""
from .classroom_api import GoogleClassroom
class MetaGroup:
    def __init__(self):
        pass

    def click_add_to_classroom(self):
        """
        Adds students to classroom. By clicking away.
        """
        pg.PAUSE = 1
        def mvclc(x, y):
            pg.moveTo(x, y)
            pg.click(x, y)
        for student in self.students:
            pg.hotkey('command', 'tab')
            pg.moveTo(1058, 530)
            pg.click()
            pg.click()
            mvclc(574, 345)
            pg.typewrite(student.email)
            pg.press('tab')
            mvclc(918, 731)
            sleep(5)

        return 0

    def add_to_classroom(self):
        """
        Add students to classroom using api
        """
