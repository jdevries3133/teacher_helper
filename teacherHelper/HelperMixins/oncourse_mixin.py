import csv

from ..tools.csv_parser import IterCsv
from ..student import Student
from ..homeroom import Homeroom
from ..parent_guardian import ParentGuardian


class OnCourseBooleanConversionError(Exception):
    pass


class OnCourseMixin:
    def __init__(self, homerooms=None, students=None, groups=None):
        self.homerooms = homerooms
        self.students = students
        self.groups = groups

    @classmethod
    def new_school_year(cls, student_data, guardian_data, strict_headers=False):
        """
        Instantiates guardians as an attribute of students. All guardians will
        never (as far as I can think) need to be accessed together, so they
        are not an attribute of the helper class.
        """
        STUDENTS = {}
        HOMEROOMS = {}

        with open(student_data, 'r', encoding='utf-8-sig') as csvfile:
            rows = [r for r in csv.reader(csvfile, delimiter=',')]
            acceptable_headers = [
                'first name',
                'last name',
                'grade level',
                'homeroom teacher',
                'email address',
            ]
            for context, row in IterCsv(acceptable_headers, rows, strict=strict_headers):
                (
                    first,
                    last,
                    grade,
                    homeroom,
                    email
                ) = (
                    row[context['first name']],
                    row[context['last name']],
                    row[context['grade level']],
                    row[context['homeroom teacher']],
                    row[context['email address']],
                )
                # convert grade to int
                for i in [4, 5, 6]:
                    if grade.find(str(i)) != -1:
                        grade = i
                        break
                student = Student(
                    {
                        'first_name': first,
                        'last_name': last,
                        'grade_level': grade,
                        'homeroom': homeroom,
                        'email': email
                    }
                )
                STUDENTS[first + ' ' + last] = student
                if homeroom not in HOMEROOMS:
                    HOMEROOMS[homeroom] = Homeroom(
                        homeroom,
                        grade,
                        [student],
                    )
                else:
                    HOMEROOMS[homeroom].students.append(student)
        # instantiation
        self = cls(
            HOMEROOMS, STUDENTS
        )
        with open(guardian_data, 'r', encoding='utf8') as csvfile:
            rows = [r for r in csv.reader(csvfile)]
            acceptable_headers = [
                'guardian first name',
                'guardian last name',
                'student first name',
                'student last name',
                'primary contact',
                'guardian email address',
                'guardian mobile phone',
                'guardian phone',
                'guardian work phone',
                'comments',
                'allow contact',
                'student resides with',
                'relation to student'
            ]
            for context, row in IterCsv(acceptable_headers, rows, strict=strict_headers):
                # create raw context dict of all strings
                if not context.get('student resides with'):
                    raise Exception(
                        'Remember, "student resides with"  is misspelled in '
                        'OnCourse. Fix it in the CSV you downloaded.'
                    )
                raw_context = {
                    'first_name': row[context.get('guardian first name')],
                    'last_name': row[context.get('guardian last name')],
                    'student': row[context.get('student first name')] + ' ' + row[context.get('student last name')],
                    'primary_contact': row[context.get('primary contact')],
                    'email': row[context.get('guardian email address')],
                    'mobile_phone': row[context.get('guardian mobile phone')],
                    'home_phone': row[context.get('guardian phone')],
                    'work_phone': row[context.get('guardian work phone')],
                    'comments': row[context.get('comments')],
                    'allow_contact': row[context.get('allow contact')],
                    'student_resides_with': row[context.get('student resides with')],
                    'relationship_to_student': row[context.get('relation to student')],
                }
                clean_context = {}
                # find student object match
                student = self.find_nearest_match(
                    raw_context['student'],
                    auto_yes=True
                )
                if not student:
                    continue
                if student.name != raw_context['student']:
                    raise Exception(
                        f"Integrity error. {student.name} does not equal "
                        + raw_context['student']
                    )
                clean_context['student'] = student
                for k, v in raw_context.items():
                    # clean phone numbers
                    if 'phone' in k:
                        if '_' in v:
                            continue
                        nums = [l for l in v if l.isnumeric()]
                        if not nums:
                            continue
                        if len(nums) < 10:
                            continue
                        if len(nums) > 11:
                            raw_context['comments'] += f'\n{k} is {v}'
                            continue
                        try:
                            phone_number = int(''.join(nums))
                            clean_context[k] = phone_number
                        except TypeError:
                            continue
                    # convert boolean fields to boolean
                    if k in [
                        'primary_contact',
                        'allow_contact',
                        'student_resides_with',
                    ]:
                        if 'Y' in v:
                            v = True
                        elif 'N' in v:
                            v = False
                        else:
                            raise OnCourseBooleanConversionError(
                                f'Supposedly boolean field {k} could not'
                                'be converted into a boolean value.'
                            )
                        clean_context[k] = v
                    clean_context.setdefault(k, v)
                parent = ParentGuardian(clean_context)
                student.guardians.append(parent)
                if clean_context['primary_contact']:
                    # It is important that the primary_contact attribute of the
                    # student is assigned while parent / guardian data is being
                    # parsed.
                    student.primary_contact = parent
        return self
