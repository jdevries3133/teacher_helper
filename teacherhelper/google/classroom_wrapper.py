import re
import logging
from typing import Any, Generator, List

from .client import get_service


logger = logging.getLogger(__name__)


class GoogleClassroomApiWrapper:
    """Wrapper for the google classroom API, which also optionally makes calls
    to the drive and slides API"""

    def __init__(
        self,
        *,
        match_assignments: List[str],
        match_classrooms: List[str],
    ):
        """`services` is a dict with keys `classroom`, `slides`, and `drive`,
        referring to the service objects from the google client APIs. Classroom
        is the only required services. If slides or drive are not passed in,
        ValueErrors will be thrown at runtime if methods that use them are
        called and they are not present.

        *match_classrooms* is a list of regex patterns for classrooms we will
        traverse. *match_assignments* is the same, but for assignments within
        classrooms. We will always traverse all student submissions.
        """
        # google client libraries are highly dynamic, so explicitly casting to
        # Any supresses type warnings
        self.classroom: Any = get_service("classroom", "v1")
        self.drive: Any = get_service("drive", "v3")
        self.slides: Any = get_service("slides", "v1")

        self._match_pats = match_classrooms
        self._match_assgt = match_assignments

        # mapping of assignment ids to teacher content, to avoid repetitive
        # google drive exports
        # TODO: implement me! this is currently unused
        self._teacher_content_cache = {}

    def get_classrooms(self) -> List[dict]:
        """Return the classrooms that match self._match_pats.

        Returns a list of courseId's that correspond to those classrooms.
        """
        courses = self.classroom.courses().list().execute()
        return self._filter_courses(courses)

    def _filter_courses(self, courses):
        ret = []
        for c in courses["courses"]:
            for p in self._match_pats:
                if re.search(p, c["name"]) is not None:
                    ret.append(c)
        return ret

    def get_assignments(self, course) -> List[dict]:
        assignments = (
            self.classroom.courses().courseWork().list(courseId=course["id"]).execute()
        )
        while token := assignments.get("nextPageToken") is not None:
            assignments += (
                self.classroom.courses()
                .courseWork()
                .list(courseId=course, nextPageToken=token)
                .execute()
            )
        return self._filter_assignments(assignments)

    def _filter_assignments(self, assignments):
        ret = []
        for c in assignments["courseWork"]:
            for p in self._match_assgt:
                if re.search(p, c["title"]) is not None:
                    ret.append(c)
        return ret

    def get_submissions(self, assignment) -> List[dict]:
        submissions = (
            self.classroom.courses()
            .courseWork()
            .studentSubmissions()
            .list(courseWorkId=assignment["id"], courseId=assignment["courseId"])
            .execute()
        )
        while token := submissions.get("nextPageToken") is not None:
            submissions += (
                self.classroom.courses()
                .courseWork()
                .studentSubmissions()
                .list(
                    courseWorkId=assignment["id"],
                    courseId=assignment["courseId"],
                    nextPageToken=token,
                )
                .execute()
            )
        return submissions["studentSubmissions"]

    def download_file(self, file_id: str, mime_type):
        return self.drive.files().export(fileId=file_id, mimeType=mime_type).execute()

    def traverse_submissions(self) -> Generator[tuple[dict, dict, dict], None, None]:
        """Yields current classroom, assignment, and submission resource
        while traversing all courseWorkSubmissions."""
        for classroom in self.get_classrooms():
            for assignment in self.get_assignments(classroom):
                for submission in self.get_submissions(assignment):
                    yield classroom, assignment, submission

    def get_student_profile(self, submission) -> dict:
        return self.classroom.userProfiles().get(userId=submission["userId"]).execute()

    def get_slides(self, submission, file) -> tuple[dict, dict]:
        """Returns a tuple of two slideshow representations: the teacher slide,
        then the student slide"""
        student_slide = (
            self.slides.presentations()
            .get(presentationId=file["driveFile"]["id"])
            .execute()
        )
        parent_id = self.find_parent_id(submission, file)
        teacher_slide = (
            self.slides.presentations().get(presentationId=parent_id).execute()
        )

        return teacher_slide, student_slide

    def find_parent_id(self, submission, file) -> str:
        """For a given file in a submission, find the parent submission from
        which it is derived. For example, navigate to the teacher template
        from a google doc that a student submitted."""

        original_assignment = (
            self.classroom.courses()
            .courseWork()
            .get(courseId=submission["courseId"], id=submission["courseWorkId"])
            .execute()
        )

        # we need to try to find the matching file from the assignment to view
        # the teacher template, or parent file, of the student submission

        n_att = len(original_assignment["materials"])

        if n_att == 0:
            raise ValueError("original assignment has no attachments")

        # if there is only one attachment on the original, we don't need to do
        # any finegaling
        if n_att == 1:
            return original_assignment["materials"][0]["driveFile"]["driveFile"]["id"]

        # google classroom uses the naming convention:
        #     <student name> - <original file name>
        # <original file name> should therefore be a substring of the student
        # file's file name. We can try to find the original by iterating over
        # all attachments.
        filename = file["driveFile"]["title"]

        for attachment in original_assignment["materials"]:
            if attachment["driveFile"]["title"] in filename:
                return attachment["driveFile"]["id"]

        raise ValueError(f"could not get content for assignment {submission}")

    def get_content(self, submission, file, mime_type="text/plain") -> tuple[str, str]:
        """For a given assignment, return the content of a submission for a
        given attachment. This returns a tuple of the teacher content, then
        the student content."""

        student_content = self.download_file(file["driveFile"]["id"], mime_type)
        parent_id = self.find_parent_id(submission, file)
        teacher_content = self.download_file(parent_id, mime_type)
        return teacher_content, student_content
