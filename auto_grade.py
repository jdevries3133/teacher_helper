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

from sparta_helper import Helper
from ClassroomAutomator import Automator

def comment_bank(ind, st):
    REQUIRED_CONTEXT = [
        'name',
    ]
    for item in REQUIRED_CONTEXT:
        if item not in context.keys():
            raise Exception(f'Missing necessary context {item}')

    comments = [
        '',  # this comment can be used to acknowledge completion of outside work

        f'Great job {st.first_name}! I hope you are using chord progressions '
        'this week in for your end-of-year music lab song!',

        f'Oops! {st.first_name}, it looks like you hit submit but forgot to '
        'put write anything in this google doc. Make sure you circle back to this, '
        'otherwise I will never know whether you did anything at all!',

        f'Oops! {st.first_name}, you were supposed to create your own unique '
        'four-chord-progression in the arpeggio maker, not chose the song whose '
        'chord progression was your favorite, although I love the chord progression '
        'of that song too!\n\nIf you get a chance, come back and make your own '
        'four-chord-progression like I did in the video, and try your best '
        'to remember what you learned about chord progressions as you work on '
        'your end-of-year music lab composition this week!',

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

def assignment_feedback_loop(helper, assignment_name, grade_level: str, scroll=0):
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
    for hr in homerooms:
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
    if TASK == 'return':
        return_work('Mixlab!', '4')
    if TASK == 'grade':
        helper = Helper.read_cache()
        for st in helper.students:
            st.outside_work = False
        assignment_feedback_loop(
            helper,
            'Chords, Arpeggios, Chord Progressions, and Harmony',
            '5',
            scroll=50
        )
        return_work(
            'Chords, Arpeggios, Chord Progressions, and Harmony',
            '5'
        )
