import code
import csv
import time
import os

import pyautogui as pg

from sparta_helper import Helper
from ClassroomAutomator import Automator

def comment_bank(ind, context):
    REQUIRED_CONTEXT = [
        'name',
    ]
    for item in REQUIRED_CONTEXT:
        if item not in context.keys():
            raise Exception(f'Missing necessary context {item}')

    comments = [
        f'Thanks {context["name"]}! I saw your post on flipgrid!',

        f'Nice job {context["name"]}! Thank you and have a great weekend!',

        'Oops! It looks like you hit "turn in," but didn\'t post anything '
        'on the flipgrid or write anything in the google doc. Please give '
        'this another look!',

        f'Thanks {context["name"]}! I saw your post on flipgrid! '
        'I appreciate that you wrote all this good stuff in the google doc '
        'too, but you only had to do the flipgrid OR the google doc!!\n'
        'Take a closer look at the directions next time, it could make your '
        'life easier!',
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
    while True:
        try:
            if st.flipgrid:
                print(f'{st.name} posted on flipgrid')
                comment = comment_bank(0, {'name': st.first_name})
                pg.typewrite(comment)
                input()
                pg.hotkey('command', 'tab')
                return 'c'
            else:
                print(f'{st.name} did not post on flipgrid')
                inp = input()
                if inp == 'b':
                    return 'b'
                if inp:
                    comment = comment_bank(int(inp), {'name': st.first_name})
                    time.sleep(0.5)
                    pg.typewrite(comment)
                    input()
                    pg.hotkey('command', 'tab')
                    return 'c'
                else:
                    pg.hotkey('command', 'tab')
                    return 'c'
        except Exception as e:
            print(f'Exception! {e}')
            return 'c'


if __name__ == '__main__':
    helper = Helper.read_cache()
    posted_on_flipgrid = []
    with open('out.csv', 'r') as csvfile:
        rd = csv.reader(csvfile)
        next(rd)
        for row in rd:
            posted_on_flipgrid.append(row[0])
    flipgrid_posters = helper.find_nearest_match(posted_on_flipgrid)
    for st in helper.students:
        if st in flipgrid_posters:
            st.flipgrid = True
        else:
            st.flipgrid = False

    username = os.getenv('GMAIL_USERNAME')
    password = os.getenv('GMAIL_PASSWORD')

    automator = Automator(username, password)
    time.sleep(2)
    homerooms = [hr for hr in helper.homerooms if hr.grade_level == '4']
    for hr in homerooms:
        done = [
            'Martinka',
            'Pitzer',
            'Spence',
        ]
        if hr.teacher not in done:
            continue
        automator.driver.get(hr.url)
        time.sleep(5)

        # get assgt url from assgt name string
        url = automator.get_assignment_link('MixLab Share!')
        automator.driver.get(url)

        # iterate through students and give feedback break on input of 'b'
        # passed to the feedback_loop function
        for _ in range(len(hr.students)):
            student_name, assignment_status = automator.clickthrough_doc(0)
            st = helper.find_nearest_match([student_name], debug=True)[0]
            msg = feedback_loop(st)
            if msg == 'b':
                break

