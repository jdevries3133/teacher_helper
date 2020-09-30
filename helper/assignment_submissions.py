import csv


class AssignmentSubmission:
    """
    Submission status codes:
        submissions can have status codes of 0, 1, or 2. Here is what they
        correspond to:

        0 = No sign of completion
        1 = Some sign of completion (a comment)
        2 = Assignment completed, but incorrectly
        3 = Unverified completion ("Turned In")
        4 = Verified completion ("Returned")

    """

    def __init__(self, title, submission):
        self.title = title
        state = submission['state']
        if state == 'CREATED':
            self.status = 0
        elif state == 'TURNED_IN':
            self.status = 3
        elif state == 'RETURNED':
            self.status = 4
        else:
            self.status = 0

    def acknowledge_comment(self, comment):
        # If I say oops, there was a mistake; downgrade assg't status
        author = comment['creator']['name']['fullName']
        if 'oops' in comment['comment'].lower() and author == 'John DeVries':
            self.status = 2
        # boost status from zero to one if student showed some engagement
        # through a comment
        if self.status == 0 and not author == 'John DeVries':
            self.status = 1


class FlipgridSubmission(AssignmentSubmission):
    """
    Important: CSVs from flipgrid must be renamed to exactly match the names
    of the corresponding assignments from google classroom.
    """

    def __init__(self, title, submission, st, csv_path):
        super().__init__(title, submission)
        with open(csv_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                if row[2] == st.first_name and row[3] == st.last_name:
                    self.status = 4


class EdpuzzleSubmission(AssignmentSubmission):
    """
    Important: CSVs from edpuzzle must be renamed to exactly match the names
    of the corresponding assignments from google classroom.
    """

    def __init__(self, title, submission, st, csv_path):
        super().__init__(title, submission)
        with open(csv_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0] == st.last_name and row[1] == st.first_name:
                    if row[3] != '0 seconds':
                        self.status = 4
