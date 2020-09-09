from .student import Student

class ParentGuardianContextError(Exception):
    pass

class ParentGuardian:
    def __init__(self, context, verbose=False):
        for i in [
            'student',
            'first_name',
            'last_name',
            'home_phone',
            'mobile_phone',
            'work_phone',
            'email',
            'relationship_to_student',
            'allow_contact',
            'student_resides_with',
        ]:
            # set attrs passed as context if they match the fields above.
            if verbose:
                for token in i.split('_'):
                    if token in context:
                        raise Warning(f'"{token}"" was passed as context, but the proper context key was "{i}."')
            context.setdefault(i, None)
            self.__setattr__(i, context[i])
        # type checking
        if not isinstance(self.student, Student):
            raise ParentGuardianContextError(
                'Student was a string, not a Student object.'
            )
        for k, v in self.__dict__.items():
            if 'phone' in k and v and not isinstance(v, int):
                breakpoint()
                raise ParentGuardianContextError(
                    'Phone number should be of type int.'
                )
        # assignment of utility attributes