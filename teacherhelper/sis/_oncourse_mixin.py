import csv
from pathlib import Path

from teacherhelper._data_dir import get_data_dir
from teacherhelper.tools.csv_parser import IterCsv
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

        with open(student_data, "r", encoding="utf-8-sig") as csvfile:
            rows = [r for r in csv.reader(csvfile, delimiter=",")]
        acceptable_headers = [
            "first name",
            "last name",
            "grade level",
            "homeroom teacher",
            "email address 1",
            "birth date",
        ]
        for get_item in IterCsv(acceptable_headers, rows):
            (first, last, grade, homeroom, email, birthday,) = (
                get_item("first name"),
                get_item("last name"),
                get_item("grade level"),
                get_item("homeroom teacher"),
                get_item("email address 1"),
                get_item("birth date"),
            )
            # convert grade to int
            for i in [4, 5, 6, 7]:
                if str(i) in grade:
                    grade = i
                    break
            student = Student(
                {
                    "first_name": first,
                    "last_name": last,
                    "grade_level": grade,
                    "homeroom": homeroom,
                    "email": email,
                    "birthday": birthday,
                }
            )
            STUDENTS[first + " " + last] = student
            if homeroom not in HOMEROOMS:
                HOMEROOMS[homeroom] = Homeroom(
                    homeroom,
                    grade,
                    [student],
                )
            else:
                HOMEROOMS[homeroom].students.append(student)

        # instantiation
        self = cls(HOMEROOMS, STUDENTS, {})  # type: ignore
        with open(guardian_data, "r", encoding="utf8") as csvfile:
            rows = [r for r in csv.reader(csvfile)]
        acceptable_headers = [
            "guardian first name",
            "guardian last name",
            "student first name",
            "student last name",
            "primary contact",
            "guardian email address 1",
            "guardian mobile phone",
            "guardian phone",
            "guardian work phone",
            "comments",
            "allow contact",
            "student resides with",
            "relation to student",
        ]
        for get_item in IterCsv(acceptable_headers, rows):
            raw_context = {
                "first_name": get_item("guardian first name"),
                "last_name": get_item("guardian last name"),
                "student": get_item("student first name")
                + " "
                + get_item("student last name"),
                "primary_contact": get_item("primary contact"),
                "email": get_item("guardian email address 1"),
                "mobile_phone": get_item("guardian mobile phone"),
                "home_phone": get_item("guardian phone"),
                "work_phone": get_item("guardian work phone"),
                "comments": get_item("comments"),
                "allow_contact": get_item("allow contact"),
                "student_resides_with": get_item("student resides with"),
                "relationship_to_student": get_item("relation to student"),
            }
            clean_context = {}
            # find student object match
            student = self.find_student(  # type: ignore
                raw_context["student"],
            )
            if not student:
                continue
            if student.name != raw_context["student"]:
                raise ValueError(
                    f"Integrity error. {student.name} does not equal "
                    + raw_context["student"]
                )
            clean_context["student"] = student
            for k, v in raw_context.items():
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
                        raw_context["comments"] += f"\n{k} is {v}"
                        continue
                    try:
                        phone_number = int("".join(nums))
                        clean_context[k] = phone_number
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
                    clean_context[k] = v
                clean_context.setdefault(k, v)
            parent = ParentGuardian(clean_context)
            student.guardians.append(parent)
            if clean_context["primary_contact"]:
                # It is important that the primary_contact attribute of the
                # student is assigned while parent / guardian data is being
                # parsed.
                student.primary_contact = parent
        return self
