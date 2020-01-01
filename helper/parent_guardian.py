from .student import Student


class ParentGuardianContextError(Exception):
    pass


class ParentGuardian:
    def __init__(self, context, verbose=False):
        self.student = context.get('student')
        self.first_name = context.get('first_name')
        self.last_name = context.get('last_name')
        self.home_phone = context.get('home_phone')
        self.mobile_phone = context.get('mobile_phone')
        self.work_phone = context.get('work_phone')
        self.email = context.get('email')
        self.relationship_to_student = context.get('relationship_to_student')
        self.primary_contact = context.get('primary_contact')
        self.allow_contact = context.get('allow_contact')
        self.student_resides_with = context.get('student_resides_with')
        try:
            self.name = self.first_name + ' ' + self.last_name
        except TypeError:
            raise ParentGuardianContextError(
                'First and last name were not provided as context to '
                'ParentGuardian class. This means that self.name cannot\n'
                'be constructed. Please at least pass a first and last name '
                'for every guardian into this class.'
            )
        for k, v in self.__dict__.items():
            if not v:
                if verbose:
                    print(
                        f'WARNING: Guardian\t{self.name}\thas no value for\t{k}'
                    )
        # type checking
        if not isinstance(self.student, Student):
            raise ParentGuardianContextError(
                'Student was a string, not a Student object.'
            )
        for k, v in self.__dict__.items():
            if 'phone' in k and v and not isinstance(v, int):
                raise ParentGuardianContextError(
                    'Phone number should be of type int.'
                )
        # assignment of utility attributes

    def __str__(self):
        outs = [
            self.relationship_to_student,
            self.name,
            f'Contact allowed: {self.allow_contact}',
            f'Is primary contact: {self.primary_contact}',
            f'Mobile Phone: {self.mobile_phone}',
            f'Email Address: {self.email}',
            '\n',
        ]
        return '\n'.join(['\t' + str(i) for i in outs if i])
