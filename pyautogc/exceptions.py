class CAException(Exception):
    """
    Inherited by all Classroom Automator Exceptions
    """


class InvalidViewError(CAException):
    """
    Called by the ClassroomAutomator.navigate_to(view) function when an invalid
    view or *args or **kwargs are ed into it.
    """


class ClassroomNameException(CAException):
    """
    Clasroom names ed in must match names in google classrooms. If a name
    ed in does not match, it will raise this exception.
    """


class AssignmentNamingConflict(Exception):
    """
    If two assignments in the same classroom have the same name.
    """
