from datetime import datetime
import json
from uuid import uuid1


def assignment_participation_audit(jsn_path, helper):
    """
    Recieves a path to a json object and a helper.
    Opens the json object, returns a modified helper object, in which the
    assignments in the json object are appended to helper.assignments, and
    each students' completion value is assigned to all matching student in
    helper.student.

    This information will be incorporated later into the CSV report.
    """
    # create a copy of the students in the classroom, and delete a student
    # from that copy every time a student is matched with a student in the helper.
    # raise an exception if there are students left in the list after all is said
    # and done.
    print('-' * 20, jsn_path, '-' * 20)
    try:
        with open(jsn_path, encoding='utf-8') as jsn:
            obj = json.load(jsn)
    except UnicodeDecodeError:
        raise Exception(f'Uncode decode error on {jsn_path}')

    """
    tree:
    obj['posts']: list
        for each
            type: dict
            keys: 'creationTime', 'courseWork'

            'courseWork': dict ... keys are: title, description, dueTime, workType, submissions

            ['courseWork']['submissions']: list
            for each: (dict) w/keys:
                student, state, assignmentSubmission

    """

    for post in obj['posts']:

        if 'courseWork' in post.keys():
            if 'submissions' not in post['courseWork'].keys():
                continue

            assgt_key = str(uuid1())
            assignment = post['courseWork']

            dst = post['creationTime'][:10].split('-')
            dtm = datetime(
                int(dst[0]),
                int(dst[1]),
                int(dst[2]),
            )
            timestamp = datetime.timestamp(dtm)
            key = assignment['title']
            if timestamp < 1583884800:
                continue

            helper.assignments.setdefault(
                key,
                {
                    'name': assignment['title'],
                    'date': timestamp,
                }
            )

            for submission in assignment['submissions']:
                if submission['state'] == 'TURNED_IN':
                    counter = 0
                    searching = True
                    while searching:
                        counter += 1
                        for st in helper.students:
                            submitter_name = submission['student']['profile']['name']['fullName']
                            if st.name == submitter_name:
                                st.assignments.setdefault(
                                    assgt_key,
                                    {'assignment_completed': True, }
                                )
                                searching = False

                            if counter > 700:
                                return Exception(f'No match found for {st.name}')

    return 0
