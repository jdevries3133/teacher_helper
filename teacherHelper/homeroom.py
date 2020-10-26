
class Homeroom:
    def __init__(self, teacher, grade_level, students):
        """
        Ensure that string constants for csv headers of id, student names, and
        (if applicable) student emails are correct.
        """
        super().__init__()
        self.teacher = teacher
        self.grade_level = grade_level
        self.students = students
