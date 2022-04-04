from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
from typing import List, Union

from .classroom_wrapper import GoogleClassroomApiWrapper
from teacherhelper.sis import Sis, Student

sis = Sis.read_cache()
logger = logging.getLogger(__name__)


@dataclass
class GradeResult:
    student: Student
    grade: int


@dataclass
class GradingContext:
    """Context that is injected into ClassroomGrader.grade_one

    All of the dicts are documented by Google:

    | member      | documentation                                                                                                          |
    | ----------- | ---------------------------------------------------------------------------------------------------------------------- |
    | course      | https://googleapis.github.io/google-api-python-client/docs/dyn/classroom_v1.courses.html                               |
    | assignment  | https://googleapis.github.io/google-api-python-client/docs/dyn/classroom_v1.courses.courseWork.html                    |
    | submissions | https://googleapis.github.io/google-api-python-client/docs/dyn/classroom_v1.courses.courseWork.studentSubmissions.html |
    | students    | https://googleapis.github.io/google-api-python-client/docs/dyn/classroom_v1.courses.students.html                      |
    """

    student: Student

    google_student: dict
    course: dict
    assignment: dict
    submission: dict


class ClassroomGrader(ABC, GoogleClassroomApiWrapper):
    """Light wrapper around GoogleClassroomApiWrapper to facilitate grading
    assignments."""

    def grade_all(self) -> List[GradeResult]:
        retval: List[GradeResult] = []

        for course, assignment, submission in self.traverse_submissions():
            try:
                google_student = self.get_student_profile(submission)
                name = google_student["name"]["fullName"]
                sis_student = sis.find_student(name)
                if not sis_student:
                    raise Exception("student not found")

                grade = self.grade_one(
                    GradingContext(
                        student=sis_student,
                        google_student=google_student,
                        course=course,
                        assignment=assignment,
                        submission=submission,
                    )
                )

                retval.append(GradeResult(student=sis_student, grade=grade))

                self.log_grade(name, grade, assignment)
            except Exception:
                student_name = self.get_student_profile(submission)["name"]["fullName"]
                logger.exception("grading failed for student named %s", student_name)
                logger.debug("assignment: %s", assignment)
                logger.debug("submission: %s", submission)

        return retval

    @abstractmethod
    def grade_one(self, context: GradingContext) -> Union[int, bool]:
        """Grade a single assignment. The return value can be boolean or int,
        depending on whether the assignment is numerically graded, or graded
        for completion only.

        Any exception thrown by this method will be handled in *grade_many*,
        and we will gracefully move on to the next student, so feel free to use
        exceptions for control flow, since those will get logged more nicely
        than quietly returning."""

    def is_form_submitted(self, submission: dict) -> bool:
        """Grading method for google forms. This assumes that the form grades
        were already imported, and it returns a boolean indicating completion
        (was the form submitted or not)"""
        return bool(submission.get("draftGrade"))

    def is_slideshow_changed(self, submission) -> bool:
        """Grading method for google slides (completion). Note that this always
        only checks the second slide, which is where I typically put my do-nows"""
        # ensure that there is exactly one attachment on the submission
        if "attachments" not in submission["assignmentSubmission"]:
            return False
        if len(submission["assignmentSubmission"]["attachments"]) < 1:
            return False
        elif len(submission["assignmentSubmission"]["attachments"]) != 1:
            logger.debug(submission)
            raise ValueError("can not grade. too many attachments")

        teacher, student = self.get_slides(
            submission,
            submission["assignmentSubmission"]["attachments"][0],
        )
        try:
            return teacher["slides"] != student["slides"]
        except KeyError:
            logger.exception("cannot compare slides")
            logger.debug("teacher %s", teacher)
            logger.debug("student %s", student)

            # fail upwards; mark the student as having done thd assignment
            return True

    def log_grade(self, name, grade, assignment):
        """Output the result of a grading action to the logger."""
        if isinstance(grade, bool):
            logger.debug(
                "{name} {status} {assignment_name}".format(
                    name=name,
                    status="completed" if grade else "did not complete",
                    assignment_name=assignment["title"],
                )
            )
        else:
            logger.debug(
                "{name} recieved grade of {grade} on {assignment_name}".format(
                    name=name, grade=grade, assignment_name=assignment["title"]
                )
            )
