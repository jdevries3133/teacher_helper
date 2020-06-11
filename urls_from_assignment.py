import csv
import json
from sparta_helper import Helper
import docx
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from pathlib import Path
import re


good_regex = re.compile(r'http(s)*://musiclab\.chromeexperiments\.com/[s|S]ong-[m|M]aker/song/(\d){16}')
near_match_regex = re.compile(r'musiclab\.chromeexperiments')

def regex_search_docx_dir(good_regex, near_match_regex, directory):
    helper = Helper.read_cache()
    matches, misses = helper.get_regex_classroom_doc(Path.resolve(Path('docs')), good_regex, yes=True, bad_link_regex=near_match_regex)
    with open('out.csv', 'w') as csvfile:
        wr = csv.writer(csvfile)
        wr.writerow(['Name', 'Link', 'Homeroom'])
        for _ in matches:
            wr.writerow(_)
    with open('fu.csv', 'w') as csvfile:
        wr = csv.writer(csvfile)
        wr.writerow(['Name', 'Link', 'Homeroom'])
        for _ in misses:
            wr.writerow(_)

def get_url_from_classroom_json():
    """
    If you want to use this again, refactor the code to take arguments. This is
    currently only written as a script.
    """
    outlinks = []
    near_match = []
    no_media = helper.find_nearest_match([
        'List students without media disclosures here.'
    ])
    for st in helper.students:
        if st in no_media:
            st.media = False
        else:
            st.media = True
    for classroom in Path.resolve(Path('smg_links')).iterdir():
        homeroom_teacher = classroom.name[:classroom.name.index('-')-1]
        print(homeroom_teacher)
        with open(classroom, 'r') as jsn:
            cls_obj = json.load(jsn)
        while True:
            hr = [hr for hr in helper.homerooms if hr.teacher == homeroom_teacher]
            if hr:
                hr = hr[0]
                break
            else:
                homeroom_teacher = input()
        for post in cls_obj['posts']:
            if 'courseWork' in post:
                if post['courseWork']['title'] == 'Make a Song for the Song Maker Gallery!!':
                    for submission in post['courseWork']['submissions']:
                        try:
                            student_name = submission['student']['profile']['name']['fullName']
                            st = helper.find_nearest_match([student_name], debug=True)[0]
                            attachments = submission['assignmentSubmission']['attachments']
                            urls  = [a['link']['url'] for a in attachments]
                        except KeyError:
                            continue
                        for url in urls:
                            mo = re.fullmatch(smg_regex, url)
                            if mo:
                                if st.media:
                                    outlinks.append([student_name, mo.string, st.homeroom, hr])
                                else:
                                    initials = st.first_name[0] + '. ' + st.last_name[0]
                                    outlinks.append([initials, mo.string, st.homeroom, hr])
                                mo = re.search(fuckup_regex, url)
                                if mo:
                                    near_match.append([student_name, mo.string, st.homeroom])
            if not 'comments' in post:
                continue
            for comment in post['comments']:
                student_name = comment['creator']['name']['fullName']
                if student_name == "John Devries":
                    continue
                try:
                    mo = re.fullmatch(smg_regex, comment['comment'])
                    if mo:
                        if st.media:
                            outlinks.append([student_name, mo.string, st.homeroom])
                        else:
                            initials = st.first_name[0] + '. ' + st.last_name[0]
                            outlinks.append([initials, mo.string, st.homeroom])
                    else:
                        mo = re.search(fuckup_regex, comment['comment'])
                        if mo:
                            near_match.append([student_name, mo.string, st.homeroom])
                            print('\n\nFuckup')
                            print([student_name, mo.string, st.homeroom])
                except Exception as e:
                    print(e)

    for hr in helper.homerooms:
        if hr.grade_level == '3':
            continue
        with open(Path('outs', hr.grade_level, f'{hr.teacher}.csv'), 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Name', 'Link'])

    for hr in helper.homerooms:
        if hr.grade_level == '3':
            continue
        with open(Path('outs', hr.grade_level, f'{hr.teacher}.csv'), 'a') as csvfile:
            writer = csv.writer(csvfile)
            for _ in outlinks:
                if _[3] == hr:
                    writer.writerow(_[:2])

    with open(Path('near_match.csv'), 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(near_match)
