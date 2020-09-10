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
