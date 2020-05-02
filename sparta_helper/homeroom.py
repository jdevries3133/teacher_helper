import csv
from datetime import datetime
import os
import re
import shelve

from student import Student

class Homeroom:
    def __init__(self, csv_path, csv_filename):
        """
        Ensure that string constants for csv headers of id, student names, and
        (if applicable) student emails are correct.
        """
        self.teacher = csv_filename[1:-4]
        self.grade_level = csv_filename[0]

        # student names and ID's in the csv
        ID_HEADER_STRING = 'ID'
        NAME_HEADER_STRING = 'Name'

        # assign indicies of id and name rows to variables "id_index" and "name
        # index."
        with open(csv_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            students = []
            id_index, name_index, = None, None
            while not (id_index or name_index):
                for row in reader:
                    for index, item in enumerate(row):
                        if item == 'ID':
                            id_index = index
                        if item == 'Name':
                            name_index = index

        self.students = []
        with open(csv_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            # instantiate a student for every student in the csv
            self.students = []
            row_check_re = re.compile(r'\d\d\d')
            for row in reader:
                if not re.search(row_check_re, row[0]):
                    continue

                # I got rid of regex, are you happy Nick?
                inverted_name = row[1]
                flip_index = inverted_name.index(',')
                last_name = inverted_name[:flip_index]
                first_name = inverted_name[(flip_index + 2):]

                context = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'student_id': int(row[0]),
                    'email': None,
                    'homeroom': csv_filename[1:-4],
                    'grade_level': csv_filename[0],
                }

                self.students.append(Student(context))


