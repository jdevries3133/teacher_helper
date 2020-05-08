from pathlib import Path
from helper import Helper

"""
Something to consider is that I am going to have weird issues if I don't
involve some sort of relational database. Right now, students are not appended
to the overall list of students if they already have been, which is good because
there are not any duplicates in helper.students. However, that also means that
the students in homeroom.students are entirely different than the ones in
choir.students. I cannot, for example, look at which students in Gorecki's
homeroom are in choir, because they are not the same student object. I think
most logical way to implement this would be with a relational database, which
is probably about due, because the picklized caching that I'm using now is
very hacky. For right now, I am just going to ignore groups; choir doesn't exist
at the moment anyway, so adding that complexity to the module serves no purpose
for now.
"""

MODULE_BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
