class CAException(Exception):
    """
    Inherited by all Classroom Automator Exceptions
    """
    pass


class InvalidViewError(CAException):
    """
    Called by the ClassroomAutomator.navigate_to(view) function when an invalid
    view or *args or **kwargs are passed into it.
    """
    pass


class ClassroomNameException(CAException):
    """
    Clasroom names passed in must match names in google classrooms. If a name
    passed in does not match, it will raise this exception.
    """
    pass

class AssignmentNamingConflict(Exception):
    """
    If two assignments in the same classroom have the same name.
    """