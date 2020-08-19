from time import sleep
import pyautogui as pg


class MetaGroup:
    """
    There are currently separate classes for homerooms and extracurricular
    activities. This meta class contains methods that apply to any type of group.
    """
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

        pg.hotkey('command', 'tab')
        for st in self.students:
            if not st.email:
                raise Exception(f'No email address for {st.name}')
            pg.moveTo(978, 463)

            """
            THIS IS USELESS

            paste_this = '\n'.join([st.email for s in students])

            Just make sure to scrub with a regex or something, because otherwise
            it won't work right.
            """

            pg.click()
            pg.click()
            mvclc(506, 301)
            pg.typewrite(st.email)
            pg.press('tab')
            mvclc(835, 682)
            sleep(5)

        return 0

    def add_to_classroom(self, username, password):
        """
        Add students to classroom using api

        Who knows if I really need username and password
        """


        session = GoogleClassroom(username, password)
