# Classroom Grader

## class `ClassroomGrader(ABC, GoogleClassroomApiWrapper): ...`

Subclass of `[GoogleClassroomApiWrapper](./classroom_wrapper.md)` to facilitate
grading assignments.

**`ClassroomGrader.grade_all(self) -> List[GradeResult]: ...`**

Iterate through all assignment submissions matching the given criteria, apply
the `grade_one` method to each submission, and return a list of [`GradeResult`](./entities.md)

**`ClassroomGrader.grade_one(...): ...`**

Full signature:

```python
@abstractmethod
def grade_one(
    self, assignment, context: Dict[Literal["course", "assignment"], dict]
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

**`ClassroomGrader.log_grade(self, name, grade, assignment): ...`**

Output the result of a grading action to the logger.
