from abc import ABC, abstractmethod
import logging
from typing import List, Union, Dict, Literal

from .classroom_wrapper import GoogleClassroomApiWrapper
from ._entities import GradeResult
from teacherhelper.sis import Sis

sis = Sis.read_cache()
logger = logging.getLogger(__name__)


class ClassroomGrader(ABC, GoogleClassroomApiWrapper):
    """Light wrapper around GoogleClassroomApiWrapper to facilitate grading
    assignments."""

    def grade_all(self) -> List[GradeResult]:
        retval: List[GradeResult] = []

        for course, assignment, submission in self.traverse_submissions():
            try:
                grade = self.grade_one(
                    assignment, {"course": course, "assignment": assignment}
                )
                name = self.get_student_profile(submission)["name"]["fullName"]
                student = sis.find_student(name)
                if not student:
                    raise Exception("student not found")

                retval.append(GradeResult(student=student, grade=grade))

                self.log_grade(name, grade, assignment)
            except Exception:
                student_name = self.get_student_profile(submission)["name"]["fullName"]
                logger.exception("grading failed for student named %s", student_name)
                logger.debug("assignment: %s", assignment)
                logger.debug("submission: %s", submission)

        return retval

    @abstractmethod
    def grade_one(
        self, assignment, context: Dict[Literal["course", "assignment"], dict]
    ) -> Union[int, bool]:
        """Grade a single assignment. Context provides the current course and
        assignment, as represented by the Google Classroom API.

        For courses, see: https://googleapis.github.io/google-api-python-client/docs/dyn/classroom_v1.courses.html
        For assignments, see: https://googleapis.github.io/google-api-python-client/docs/dyn/classroom_v1.courses.courseWork.html
        For submissions, see: https://googleapis.github.io/google-api-python-client/docs/dyn/classroom_v1.courses.courseWork.studentSubmissions.html
        """

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
