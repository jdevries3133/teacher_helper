import csv
from pathlib import Path

from teacherhelper._data_dir import get_data_dir
from ._entities import Homeroom, ParentGuardian, Student


class OnCourseMixin:
    """This doesn't specifically interface with the OnCourse API, it just
    initializes the helper cache with the spreadsheet reports that I output
    from oncourse, using those specific headers."""

    @classmethod
    def new_school_year(cls):
        """Take a spreadsheet of student data and parent data, build the
        necessary relationships.

        Student data csv should include columns:

        - first name
        - last name
        - grade level
        - homeroom teacher
        - email address 1
        - birth date

        Parent data csv should include:

        - guardian first name
        - guardian last name
        - student first name
        - student last name
        - primary contact
        - guardian email address 1
        - guardian mobile phone
        - guardian phone
        - guardian work phone
        - comments
        - allow contact
        - student resides with
        - relation to student
        """
        student_data = Path(get_data_dir(), "students.csv")
        guardian_data = Path(get_data_dir(), "parents.csv")
        STUDENTS = {}
        HOMEROOMS = {}

        # various adapters from grade level representations to int
        to_number = {"4th Grade": 4, "5th Grade": 5, "6th Grade": 6, "7th Grade": 7}

        with open(student_data, "r", encoding="utf-8-sig") as csvfile:
            rd = csv.DictReader(csvfile)
            for row in rd:
                # convert keys to lowercase to normalize case
                row = {k.lower(): v for k, v in row.items()}
                student = Student(
                    {
                        "first_name": row.get("first name"),
                        "last_name": row.get("last name"),
                        "grade_level": to_number[row.get("grade level", "")],
                        "homeroom": row.get("homeroom teacher"),
                        "email": row.get("email address 1"),
                        "birthday": row.get("birth date"),
                    }
                )
                STUDENTS[student.name] = student
                if student.homeroom not in HOMEROOMS:
                    HOMEROOMS[student.homeroom] = Homeroom(
                        student.homeroom,
                        student.grade_level,
                        [student],
                    )
                else:
                    HOMEROOMS[student.homeroom].students.append(student)

        # instantiation
        self = cls(HOMEROOMS, STUDENTS, {})  # type: ignore
        with open(guardian_data, "r", encoding="utf8") as csvfile:
            rd = csv.DictReader(csvfile)
            for row in rd:
                # normalize headers to lowercase
                row = {k.lower(): v for k, v in row.items()}
                context = {
                    "first_name": row.get("guardian first name"),
                    "last_name": row.get("guardian last name"),
                    "student": (
                        row.get("student first name", "")
                        + " "
                        + row.get("student last name", "")
                    ),
                    "primary_contact": row.get("primary contact"),
                    "email": row.get("guardian email address 1"),
                    "mobile_phone": row.get("guardian mobile phone"),
                    "home_phone": row.get("guardian phone"),
                    "work_phone": row.get("guardian work phone"),
                    "comments": row.get("comments"),
                    "allow_contact": row.get("allow contact"),
                    "student_resides_with": row.get("student resides with"),
                    "relationship_to_student": row.get("relation to student"),
                }
                # find student object match
                student = self.find_student(context["student"])  # type: ignore
                if not student:
                    continue
                if student.name != context["student"]:
                    raise ValueError(
                        f"Integrity error. {student.name} does not equal "
                        + context["student"]
                    )
                context["student"] = student

                for k, v in context.items():
                    # clean phone numbers
                    if "phone" in k:
                        if "_" in v:
                            continue
                        nums = [l for l in v if l.isnumeric()]
                        if not nums:
                            continue
                        if len(nums) < 10:
                            continue
                        if len(nums) > 11:
                            context["comments"] += f"\n{k} is {v}"
                            continue
                        try:
                            phone_number = int("".join(nums))
                            context[k] = phone_number
                        except TypeError:
                            continue
                    # convert boolean fields to boolean
                    if k in [
                        "primary_contact",
                        "allow_contact",
                        "student_resides_with",
                    ]:
                        if "Y" in v:
                            v = True
                        elif "N" in v:
                            v = False
                        else:
                            raise ValueError(
                                f"Supposedly boolean field {k} could not"
                                "be converted into a boolean value."
                            )
                        context[k] = v

                parent = ParentGuardian(context)
                student.guardians.append(parent)
                if context["primary_contact"]:
                    student.primary_contact = parent

        return self
