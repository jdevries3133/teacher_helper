from abc import ABC, abstractmethod
import logging
from typing import Dict, List, Literal

from .google_classroom import GoogleClassroomApiWrapper
from ._entities import GradeResult
from .sis_proxy import sis


logger = logging.getLogger(__name__)


class ClassroomGrader(ABC):
    def __init__(
        self,
        services,
        *,
        assignment_name,
        match_classrooms,
        match_assignments,
    ):
        """See `GoogleClassroom` for details on `services`. `assignment_name`
        is the value placed into the `GradeResult` objects returned by
        `ClassroomGrader.grade_assignments`
        """
        self.classroom = GoogleClassroomApiWrapper(
            services,
            match_classrooms=match_classrooms,
            match_assignments=match_assignments,
        )
        self.assignment_name = assignment_name

    def grade_assignments(self) -> List[GradeResult]:
        result_map = {}
        for _, assignment, submission in self.classroom.traverse_submissions():
            try:
                method = self.grading_method(assignment)
                grade = method(submission)  # type: ignore
                name = self.classroom.get_student_profile(submission)["name"][
                    "fullName"
                ]

                result_map.setdefault(name, {})
                result_map[name][assignment["title"]] = grade

                self.log_grade(name, grade, assignment)
            except Exception:
                logger.exception("grading failed")
                logger.debug("assignment: %s", assignment)
                logger.debug("submission: %s", submission)

        retval: List[GradeResult] = []

        for name, result in result_map.items():
            n_complete = 0
            for grade in result.values():
                if grade:
                    n_complete += 1
            # TODO: leaky abstraction; this should be a separate method
            n_complete_to_grade: Dict[int, Literal[0, 15, 20]] = {0: 0, 1: 15, 2: 20}
            student = sis.find_nearest_match(name)  # type: ignore
            if student is None:
                logger.warning("no match for %s. skipping", name)
                continue

            # TODO: consequences of the leaky abstraction
            grade = n_complete_to_grade[n_complete]
            if student.grade_level == 5 and "Week 21" in result:
                if n_complete > 0:
                    grade = 20
                else:
                    grade = 0
            retval.append(
                GradeResult(
                    student=student, assignment=self.assignment_name, grade=grade
                )
            )

        return retval

    @abstractmethod
    def grading_method(self, assignment):
        """For a given assignment, return the correct grading method"""

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

        teacher, student = self.classroom.get_slides(
            submission,
            submission["assignmentSubmission"]["attachments"][0],
        )
        try:
            return teacher["slides"][1] != student["slides"][1]
        except KeyError:
            logger.exception("cannot compare slides")
            logger.debug("teacher %s", teacher)
            logger.debug("student %s", student)

            # fail upwards; mark the student as having done thd assignment
            return True

    def log_grade(self, name, grade, assignment):
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
