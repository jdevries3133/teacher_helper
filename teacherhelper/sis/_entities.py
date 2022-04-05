class Group:
    """
    Group class is used to manage groups for extracurricular activities, field
    trips, and other purposes.
    """

    def __init__(self, name, grade_level, students):
        self.name = name
        self.grade_level = grade_level
        self.students = students


class Homeroom:
    def __init__(self, teacher, grade_level, students):
        """
        Ensure that string constants for csv headers of id, student names, and
        (if applicable) student emails are correct.
        """
        self.teacher = teacher
        self.grade_level = grade_level
        self.students = students


class Student:
    def __init__(self, context):
        context.setdefault("groups", [])
        context.setdefault("guardians", [])
        self.first_name = context.get("first_name")
        self.last_name = context.get("last_name")
        self.student_id = context.get("student_id")
        self.homeroom = context.get("homeroom")
        self.grade_level = context.get("grade_level")
        self.groups = context.get("groups")
        self.email = context.get("email")
        self.guardians = context.get("guardians")
        self.name = self.first_name + " " + self.last_name

        # primary_contact is an instance of ParentGuardian, which is assigned
        # during the parsing of parent / guardian data in the new_school_year
        # function within OnCourseMixin
        # TODO: assign attribute at init time, not later
        self.primary_contact = None

    def __eq__(self, other):
        if not isinstance(other, Student):
            return False

        if self.email is not None:
            return self.email == other.email

        if self.name is not None:
            return self.name == other.name

        raise ValueError("insufficient attributes to compare")

    def __str__(self, verbose=False):
        """
        Assemble nice printout of student information, and student's guardian
        information. Also, offer verbose option, which ties into /shell.py
        """
        data = [
            "--",
            self.name,
            self.grade_level,
            self.homeroom,
            self.email,
            "--" "\nGuardians:",
        ]
        student_data = [str(i) for i in data if i]  # filter out NoneTypes
        if not self.guardians:
            return "\n".join(data)
        # indent
        gu_data = ["\n\t".join(self.primary_contact.__str__().split("\n"))]
        cutoff = 3 if not verbose else len(self.guardians) - 1
        for gu in self.guardians[1:cutoff]:
            gu_data.append("\n\t".join(gu.__str__().split("\n")))
        return "\n".join(student_data + gu_data)

    def __repr__(self):
        normal = super().__repr__()
        return normal.replace("object", f'"{self.name}" object')


class ParentGuardian:
    def __init__(self, context: dict, verbose=False):

        self.student = context.get("student")
        self.first_name = context.get("first_name")
        self.last_name = context.get("last_name")
        self.home_phone = context.get("home_phone")
        self.mobile_phone = context.get("mobile_phone")
        self.work_phone = context.get("work_phone")
        self.email = context.get("email")
        self.relationship_to_student = context.get("relationship_to_student")
        self.primary_contact = context.get("primary_contact")
        self.allow_contact = context.get("allow_contact")
        self.student_resides_with = context.get("student_resides_with")

        # full name
        if self.first_name and self.last_name:
            self.name = self.first_name + " " + self.last_name
        else:
            raise ValueError(
                "First and last name were not provided as context to "
                "ParentGuardian class. This means that self.name cannot\n"
                "be constructed. Please at least pass a first and last name "
                "for every guardian into this class."
            )

        # warn about missing attributes
        for k, v in self.__dict__.items():
            if not v:
                if verbose:
                    print(f"WARNING: Guardian\t{self.name}\thas no value for\t{k}")

        # type checking
        if not isinstance(self.student, Student):
            raise ValueError("Student was a string, not a Student object.")

    def __str__(self):
        outs = [
            self.relationship_to_student,
            self.name,
            f"Contact allowed: {self.allow_contact}",
            f"Is primary contact: {self.primary_contact}",
            f"Mobile Phone: {self.mobile_phone}",
            f"Email Address: {self.email}",
            "\n",
        ]
        return "\n".join([str(i) for i in outs if i])
