"""Proxy module to ensure that the student information object is a singleton
throughout this module. This is critical so that overrides applied in __main__
propagate throughout the module and are not wiped out every time a new helper is
created with `Helper.read_cache()`"""

from teacherhelper.sis import Sis

sis = Sis.read_cache()
