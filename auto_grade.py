"""
The script helps with grading in google classroom. It can grade the same assignment
across multiple classrooms by iterating through homerooms of the appropriate
grade level. The script uses two constants, assignment name, and grade level.
It is also necessary to rewrite the comment bank for the given assignment.

Within the __name__ == '__main__' block, you can do many tricky things. For
example, you can incorporate acknowledgement for student completion of outside
work. Also, you can assign any attribute on the student object which can be
accessed later by the comment bank.
"""

import time
import os

import pyautogui as pg
import pyperclip as pc

from helper import Helper
from ClassroomAutomator import Automator

ASSIGNMENT_NAME = 'Reverse, Reverse!'
GRADE_LEVEL = '5'
GOOGLE_DOC_SCROLL = 200

def comment_bank(ind, st):

    comments = [
        '',  # this comment can be used to acknowledge completion of outside work

        f'Awesome job {st.first_name}! I know that this assignment was extremely '
        'difficult — more difficult than I intended, and I\'m sorry for that! '
        'However, I can see that you gave this assignment your best shot, and '
        'you did a really good job!\n\nHave a great week, and thanks for your '
        'hard work in music throughout the craziness of the past months!',

        f'Wow {st.first_name}, this assignment was super difficult and you '
        'nailed it, amazing job! I\'m sorry that this assignment was so tricky, '
        'but I can see that you rose to the occasion. Have a great week, and '
        'thank you for your hard work in music class throughout the craziness '
        'of the past months!'
    ]
    try:
        comments[ind]
    except IndexError:
        print('no matching comment')
        return ''
    return comments[ind]

def feedback_loop(st):
    """
    returns 'c' for continue, or 'b' for break. When you get to the end
    of students who have completed their assignments, you may want to
    skip to the next homeroom. That can be accomplished by simply entering
    'b' for break. As a result, the function will return 'b', and the loop
    within which it is placed can be told to break.
    """
    pg.PAUSE = 1
    while True:
        if st.outside_work:
            print(f'{st.name} did the outside work.')
            comment = comment_bank(0, st)
            pg.typewrite(comment)
            input()
            pg.hotkey('command', 'tab')
            return 'c'
        else:
            print(f'{st.name} did not do any outside work.')
            inp = input()
            if inp == 'b':
                return 'b'
            if inp:
                try:
                    int(inp)
                except ValueError:
                    return 'c'
                comment = comment_bank(int(inp), st)
                pg.hotkey('command', 'tab')
                time.sleep(0.5)
                pc.copy(comment)
                pg.hotkey('command', 'v')
                input()
                pg.hotkey('command', 'tab')
                time.sleep(0.3)
                return 'c'
            else:
                pg.hotkey('command', 'tab')
                time.sleep(0.3)
                return 'c'

def return_work(assignment_name, grade_level: str):
    username = os.getenv('GMAIL_USERNAME')
    password = os.getenv('GMAIL_PASSWORD')
    helper = Helper.read_cache()
    automator = Automator(username, password)
    homerooms = [hr for hr in helper.homerooms if hr.grade_level == grade_level]
    for index, hr in enumerate(homerooms):
        print(('*' * 30), f'{index} of {len(homerooms)} homerooms complete', ('*' * 30))
        url = automator.get_assignment_link(hr.url, assignment_name)
        url = url.split('/')
        url = f'https://classroom.google.com/c/{url[5]}/a/{url[6]}/submissions/by-status/and-sort-name/all'
        automator.driver.get(url)
        input()
        pg.hotkey('command', 'tab')
    automator.driver.close()

def assignment_feedback_loop(helper, assignment_name, grade_level: str, scroll=0, start_on=0):
    """
    Assignment name must be exactly correct, case sensitive. There is no error
    handling.
    """
    st_set = [st for st in helper.students if st.grade_level == grade_level]
    for st in st_set:
        if not hasattr(st, 'outside_work'):
            raise Exception(
                'You must set outside_work attr to true or false for each student '
                'before passing them to the feedback loop. If there is no outside '
                'work, set every student to false first.'
            )
    username = os.getenv('GMAIL_USERNAME')
    password = os.getenv('GMAIL_PASSWORD')
    automator = Automator(username, password)
    homerooms = [hr for hr in helper.homerooms if hr.grade_level == grade_level]
    for index, hr in enumerate(homerooms):
        if index <= start_on:
            continue
        print(('*' * 30), f'{index} of {len(homerooms)} homerooms complete', ('*' * 30))
        url = automator.get_assignment_link(hr.url, assignment_name)
        automator.driver.get(url)
        for _ in range(len(hr.students)):
            try:
                student_name, assignment_status = automator.clickthrough_doc(scroll)
            except Exception as e:
                print(f'Unhandled exception: {e}')
                continue
            st = helper.find_nearest_match([student_name])[0]
            msg = feedback_loop(st)
            if msg == 'b':
                break
    automator.driver.close()

if __name__ == "__main__":
    helper = Helper.read_cache()
    for st in helper.students:
        st.outside_work = False
    assignment_feedback_loop(
        helper,
        ASSIGNMENT_NAME,
        GRADE_LEVEL,
        GOOGLE_DOC_SCROLL,
    )
    return_work(
        ASSIGNMENT_NAME,
        GRADE_LEVEL,
    )
