"""Before being called SIS (Student Information System), the sis module was
just called `helper`, and it was basically the full scope of the library. This
module adapts from the new API to that old one."""

from typing import Union
import warnings

from .sis import Sis, Student


class Helper(Sis):
    def __init__(self, *a, **kw):
        super().__init__(*a, *kw)
        warnings.warn(
            "Helper interface is deprecated. Use teacherhelper.Sis instead.",
            DeprecationWarning,
        )

    def find_nearest_match(
        self, student_name: str, threshold=90, **_
    ) -> Union[Student, None]:
        return self.find_student(student_name, threshold)

    def find_parent(self, parent_name: str) -> Union[Student, None]:
        result = super().find_parent(parent_name)
        if result:
            return result.student

    @classmethod
    def read_cache(cls, *a, **kw):
        warnings.warn(
            "Helper interface is deprecated. Use teacherhelper.Sis instead.",
            DeprecationWarning,
        )
        return super().read_cache(*a, **kw)


def get_helper() -> Helper:
    return Helper.read_cache()
