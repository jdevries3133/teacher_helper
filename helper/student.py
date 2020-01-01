class Student:
    def __init__(self, context):
        context.setdefault('groups', [])
        context.setdefault('guardians', [])
        self.first_name = context.get('first_name')
        self.last_name = context.get('last_name')
        self.student_id = context.get('student_id')
        self.homeroom = context.get('homeroom')
        self.grade_level = context.get('grade_level')
        self.groups = context.get('groups')
        self.email = context.get('email')
        self.guardians = context.get('guardians')
        self.name = self.first_name + ' ' + self.last_name
        """
        primary_contact is an instance of ParentGuardian, which is assigned
        during the parsing of parent / guardian data in the new_school_year
        function within OnCourseMixin
        """
        self.primary_contact = None

    def __str__(self, verbose=False):
        """
        Assemble nice printout of student information, and student's guardian
        information. Also, offer verbose option, which ties into /shell.py
        """
        data = [
            '--',
            self.name,
            self.grade_level,
            self.homeroom,
            self.email,
            '--'
            '\nGuardians:'
        ]
        data = [str(i) for i in data if i]  # filter out none
        if not self.guardians:
            return '\n'.join(data)
        gu_data = [self.primary_contact]
        cutoff = 2 if not verbose else len(self.guardians)
        for gu in self.guardians[1:]:
            raw = [
                '...',
                gu.relationship_to_student,
                gu.name,
                f'Contact allowed: {gu.allow_contact}',
                f'Is primary contact: {gu.primary_contact}',
                gu.mobile_phone,
                gu.email,
                '\n',
            ]
            app = ['\t' + str(i) for i in raw[1:] if i]
            gu_data += app
        return '\n'.join(data + gu_data)
