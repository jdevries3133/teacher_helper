import os

import requests

def get_session():
    """
    Make a session and log in.
    """
    session = requests.Session()
    session.get('https://genesis.sparta.org/sparta/sis/view?gohome=true')

    username = os.getenv('GENESIS_USERNAME')
    password = os.getenv('GENESIS_PASSWORD')
    if not username or not password:
        raise Exception(
            f'"GENESIS_USERNAME and GENESIS_PASSWORD must be defined environment variables for '
            'genesis authentication.'
        )

    request = requests.Request(
        'POST',
        'https://genesis.sparta.org/sparta/sis/j_security_check',
        data={
            'j_username': username,
            'j_password': password
        },
    )
    session.send(request.prepare())

    return session

class SpartaHelper(helper):
    """
    Helper methods that were only relevant in sparta.
    """
    def __init__(self, homerooms, students, groups):
        super().__init__(homerooms, students, groups)

    @classmethod
    def genesis_new_school_year(cls, csvdir):
        """
        Pass an absolute path to a directory full of csv files for all homerooms
        and miscellaneous groups. Note that these CSV files must follow a
        fairly strict naming convention as described in this module's readme.
        """
        homerooms = []
        students = []
        groups = []
        # deal with all homerooms, pass over groups
        for filename in os.listdir(csvdir):
            # skip .DS_store and other nonsense
            if '.csv' not in filename:
                continue
            path_to_csv = Path(csvdir, filename)
            # call parsing functions
            if path_to_csv.stem[0] == 'h':
                teacher, grade_level, this_students = parse_homeroom(path_to_csv)
                for st in copy(this_students):
                    if st.student_id in [s.student_id for s in students]:
                        match = Helper.get_matching_student(st, students, homeroom.teacher)
                        this_students.remove(st)
                        this_students.append(match)
                    else:
                        students.append(st)
                homeroom = Homeroom(teacher, grade_level, this_students)
                homerooms.append(homeroom)
                print('homeroom', homeroom.teacher, 'has', str(len(homeroom.students)), 'students')
            elif path_to_csv.stem[0] == 'g':
                # deal with groups once all the homerooms are done to help
                # with the duplicate student problem
                continue
            else:
                raise Exception(f'Unable to parse file: {filename}')
        for filename in os.listdir(csvdir):
            # skip .DS_store and other nonsense
            if '.csv' not in filename:
                continue
            path_to_csv = Path(csvdir, filename)
            if path_to_csv.stem[0] == 'g':
                name, grade_level, this_students = parse_group(path_to_csv)
                for st in copy(this_students):
                    if st.name in [s.name for s in students]:
                        match = Helper.get_matching_student(st, students)
                        match.groups += st.groups
                        this_students.remove(st)
                        this_students.append(match)
                    else:
                        students.append(st)
                group = Group(name, grade_level, this_students)
                groups.append(group)
        new_helper = cls(homerooms, students, groups)
        new_helper.write_cache()
        return new_helper 