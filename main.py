from copy import copy
import csv
from random import randint

from sparta_helper import Helper

helper = Helper.read_cache()
import sys
sys.exit()
with open('/Users/JohnDeVries/Downloads/Soundtrap\ Parent\ Permission\ Form.csv', 'r') as csvfile:
    rd = csv.reader(csvfile)
    with open('out.csv', 'w') as csvout:
        wr = csv.writer(csvout)
        matches = []
        for rd_row in rd:
            if rd_row[4][0] == 'D':
                pass

            for st in helper.students:
                if st.last_name == rd_row[3]:
                    print(f'match found for {rd_row}')
                    matches.append(st)

            if rd_row[3] not in [s.last_name for s in helper.students]:
                print(r'***no match {rd_row}')

        wr.writerow(['First name', 'Last name', 'Email', 'Password'])
        for st in matches:
            password = f'{student.last_name + student.first_name[0] + randint(10, 99)}',
            wr.writerow([
                st.first_name,
                st.last_name,
                st.email,
                password,
            ])

        with open('html_template.html', 'r') as template_io:
            template = template_io.read()

        template.replace('{username}', st.email)
        template.replace('{password}', password)

        file_ind = st.email.index('@')
        with open(f'{st.email[:file_ind].html}', 'w') as email:
            email.write(template)

