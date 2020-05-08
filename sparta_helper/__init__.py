from .helper import Helper
from .homeroom import Homeroom
from .student import Student

def cache_reader():
    return Helper.read_cache()
