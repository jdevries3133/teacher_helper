import os

from homeroom import Homeroom
from student import Student

MODULE_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

homerooms = []
for filename in os.listdir(os.path.join(MODULE_BASE_DIR, 'source_data', 'homerooms')):
    print(os.path.abspath(filename))
    abspath = os.path.join(MODULE_BASE_DIR, 'source_data', 'homerooms', filename)
    homerooms.append(Homeroom(abspath, filename))

for hr in homerooms:
    for st in hr.students:
        st.get_email()
