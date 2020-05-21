import csv
import os
from pathlib import Path

from sparta_helper import Helper, Student

if __name__ == 'ph':
    helper = Helper.read_cache()

    unres_pths = [
        Path('google_classrooms'),
        Path('flipgrid'),
        Path('edpuzzle'),
    ]

    pths = [Path.absolute(p) for p in unres_pths]
    helper.find_non_participators(pths)

if __name__ == '__main__':
    path_in = Path.resolve(Path('.', 'soundtrap_in.csv'))
    path_out = Path.resolve(Path('.', 'soundtrap_out.csv'))
    path_update = Path.resolve(Path('.', 'soundtrap_update.csv'))

    helper = Helper.read_cache()
    #students = helper.soundtrap_update(path_in, path_out, path_update, debug=True)

    with open(path_out, 'r') as csv_send_cred:
        rd = csv.reader(csv_send_cred)
        next(rd)
        students = []
        for row in rd:
            student = Student(context={
                'first_name': row[0],
                'last_name': row[1],
                'email': row[2],
            })
            student.soundtrap_password = row[3]
            students.append(student)
            print(student.soundtrap_password)


    helper.email(students, 'soundtrap')



    