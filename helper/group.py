from .meta_groups import MetaGroup

class Group(MetaGroup):
    """
    Group class is used to manage groups for extracurricular activities, field
    trips, and other purposes.
    """
    def __init__(self, name, grade_level, students):
        self.name = name
        self.grade_level = grade_level
        self.students = students
