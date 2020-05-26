import csv
import os
import re
from pathlib import Path

from sparta_helper import Helper

if __name__ == "__main__":
    helper = Helper.read_cache()
    classrom_path = Path.resolve(Path('.', 'google_classrooms'))
    assgt_reg = re.compile(r'Mixlab!')
    helper.from_classroom(assgt_reg, 'assignment', 'mixlab_submission', classrom_path)

    submissions = []
    for st in helper.students:
        if hasattr(st, 'mixlab_submission'):
            try:
                submissions.append({
                    'name': st.name,
                    'link': st.mixlab_submission['assignmentSubmission']['attachments'][0]['link']['url']
                })
                print('\n\nSUCCESS\n\n')
            except KeyError:
                print(f'key error on {st.__dict__}')
                pass

    with open('out.csv', 'w') as csvfile:
        wr = csv.writer(csvfile)
        for subm in submissions:
            wr.writerow([subm['name'], subm['link']])