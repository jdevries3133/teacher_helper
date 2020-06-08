import code
import csv
import time
import os

import pyautogui as pg
import pyperclip as pc

from sparta_helper import Helper
from ClassroomAutomator import Automator

TASK = 'grading'

def comment_bank(ind, context):
    REQUIRED_CONTEXT = [
        'name',
    ]
    for item in REQUIRED_CONTEXT:
        if item not in context.keys():
            raise Exception(f'Missing necessary context {item}')

    comments = [
        '',

        f'Nice job {context["name"]}! I really like the chord progression that '
        'you used. I hope that you are using what you learned in your composition '
        'for this week!\n\n'
        'Here is a sneak peek of the gallery that I am going to '
        'use to display your compositions after they\'re all turned in this week! '
        'https://songmakergallery.com/gallery/sample-gallery/',

        f'Oops! {context["name"]}, it looks like you forgot to attach your link '
        'to this assignment. That is ok, but MAKE SURE you don\'t make the same '
        'mistake this week! If you do, your composition won\'t end up in our gallery!\n\n'
        'By the way, here is a sneak peek of what the song maker gallery is going '
        'to look like! https://songmakergallery.com/gallery/sample-gallery/\n\n',

        f'Hey there {context["name"]}, nice job! I like the chord progression '
        'that you created, and you did a great job following the video and '
        'completing the assignment.\n\nThis is a nitpicky thing, but I notice that '
        'you pasted your link into a google doc. Next time, make sure you attach '
        'your link directly to the assignment. That will be super important to me '
        'this week so that I can get your composition into the Song Maker Gallery!\n\n'
        'By the way, here is a sneak peek of what that is going to look like! '
        'https://songmakergallery.com/gallery/sample-gallery/',

    ]

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
            comment = comment_bank(0, {'name': st.first_name})
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
                comment = comment_bank(int(inp), {'name': st.first_name})
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
    for hr in homerooms:
        url = automator.get_assignment_link(hr.url, assignment_name)
        url = url.split('/')
        url = f'https://classroom.google.com/c/{url[5]}/a/{url[6]}/submissions/by-status/and-sort-name/all'
        automator.driver.get(url)
        input()
        pg.hotkey('command', 'tab')

def assignment_feedback_loop(helper, assignment_name, grade_level: str):
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

        # get assgt url from assgt name string
        url = automator.get_assignment_link(hr.url, assignment_name)
        automator.driver.get(url)

        # iterate through students and give feedback break on input of 'b'
        # passed to the feedback_loop function
        for _ in range(len(hr.students)):
            student_name, assignment_status = automator.clickthrough_doc(0)
            st = helper.find_nearest_match([student_name])[0]
            msg = feedback_loop(st)
            if msg == 'b':
                break

if __name__ == "__main__":
    if TASK == 'return':
        return_work('Chords in the Song Maker', '5')
    if TASK == 'grade':
        helper = Helper.read_cache()
        for st in helper.students:
            st.outside_work = False
        assignment_feedback_loop(helper, 'Chords in the Song Maker', '5')