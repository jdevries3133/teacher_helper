import csv
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
    def new_school_year(cls, student_data, guardian_data):
        """
        Instantiates guardians as an attribute of students. All guardians will
        never (as far as I can think) need to be accessed together, so they
        are not an attribute of the helper class.
        """
        STUDENTS = {}
        HOMEROOMS = {}
        with open(student_data, 'r', encoding='utf8') as csvfile:
            rd = csv.reader(csvfile, delimiter=',')
            next(rd)  # skip header
            for row in rd:
                (
                    first,
                    last,
                    grade,
                    homeroom,
                    email
                ) = row
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
            rd = csv.reader(csvfile)
            next(rd)
            for row in rd:
                # create raw context dict of all strings
                raw_context = {
                    'first_name': row[0],
                    'last_name': row[1],
                    'student': row[2] + ' ' + row[3],
                    'primary_contact': row[4],
                    'email': row[5],
                    'mobile_phone': row[6],
                    'home_phone': row[7],
                    'work_phone': row[8],
                    'comments': row[9],
                    'allow_contact': row[10],
                    'student_resides_with': row[11],
                    'relationship_to_student': row[12],
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
                    student.primary_contact = parent
        return self
