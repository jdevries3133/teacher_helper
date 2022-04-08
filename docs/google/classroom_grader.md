# Classroom Grader

> ### Note!
>
> You will need to setup oauth credentials on the Google Cloud Platform and
> provide those credentials to this library before you can use this module.

<blockquote style="background-color: #fedada">
  <h3>Warning</h3>
  <p>
      This module does not have thorough unit tests yet. Please validate the
      results with care, report bugs that you find, and consider contributing some
      tests!
  </p>
</blockquote> See documentation on the [client wrapper](./client.md) for directions.

## Module `teacherhelper.google.classroom_grader`

Uses GoogleClassroomApiWrapper to create a framework for grading assignments.

## dataclasses

**`GradeResult`**

```python
@dataclass
class GradeResult:
    student: Student
    grade: int
```

**`GradingContext`**

```python
@dataclass
class GradingContext:
    student: Student

    google_student: dict
    course: dict
    assignment: dict
    submission: dict
```

_google_student_, _course_, _assignment_, and _submission_ are all data
structures emitted by Google's API, and are documented by Google:

- [course](https://googleapis.github.io/google-api-python-client/docs/dyn/classroom_v1.courses.html)
- [assignment](https://googleapis.github.io/google-api-python-client/docs/dyn/classroom_v1.courses.courseWork.html)
- [submissions](https://googleapis.github.io/google-api-python-client/docs/dyn/classroom_v1.courses.courseWork.studentSubmissions.html)
- [students](https://googleapis.github.io/google-api-python-client/docs/dyn/classroom_v1.courses.students.html)

## class `teacherhelper.google.classroom_grader.ClassroomGrader(ABC, GoogleClassroomApiWrapper): ...`

Subclass of [`GoogleClassroomApiWrapper`](./classroom_wrapper.md) to facilitate
grading assignments.

**`ClassroomGrader.grade_all(self) -> List[GradeResult]: ...`**

Iterate through all assignment submissions matching the given criteria, apply
the `grade_one` method to each submission, and return a list of
[`GradeResult`.](#dataclasses)

**`ClassroomGrader.grade_one(...): ...`**

Full signature:

```python
def grade_one(
    self,
    assignment,
    context: Dict[Literal["course", "assignment", "student"], dict],
) -> Union[int, bool]:
```

**Abstract method** which grades a particular assignment. You can do whatever
you want here with the information it delivers you for each matching student
submission. The return value can be boolean or int, depending on whether the
assignment is numerically graded, or graded for completion only.

The utility methods documented below are ideally used inside this method.

**`ClassroomGrader.is_form_submitted(self, submission: dict) -> bool: ...`**

Grading method for google forms. This assumes that the form grades were already
imported, and it returns a boolean indicating completion (was the form
submitted or not). Not super useful on its own, because obviously Google Forms
are self-grading, but it can be helpful if you're writing a script to grade
several assignments, then combining it into some larger output.

**`ClassroomGrader.is_slideshow_changed(self, submission) -> bool: ...`**

Grading method for google slides (completion).

**`ClassroomGrader.log_grade(self, name, grade, assignment) -> None: ...`**

Output the result of a grading action to the logger.
