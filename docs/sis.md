# Student Information System

`teacherhelper.sis` forms a student information system inside Python. Data
should be imported through the process described in [setup docs.](../setup/)

## class `teacherhelper.sis.Sis`

The student information system through which most of the information below
can be accessed. Again, there is a [setup procedure](../setup) for initially
populating the class with data. Normally, when you use this in scripts, you
will use the `read_cache` classmethod for initialization, which loads the
pickled class from the data directory, as described in the setup docs.

**`Sis.__init__(...)`**

Full signature:

```python
def __init__(
    self,
    homerooms: dict[str, Homeroom],
    students: dict[str, Student],
    groups: dict[str, Group],
): ...
```

If you are calling this, that means that you are initializing all the entities
on your own somehow. Usually, you won't use this, and will use the
`Sis.new_school_year` method instead, which will do all the initialization for
you using csv files in the data folder.

**`Sis.find_student(self, student_name: str, threshold: int=90) -> Union[Student, None]: ...`**

Returns a student object. Optionally, set a Levenshtien distance threshold
below which students will not be included.

**`Sis.find_parent(self, parent_name: str, threshold: int=70) -> Union[ParentGuardian, None]: ...`**

Return a parent matching the given name, preferentially searching
amongst primary contacts. This uses fixed thresholds internally.

#### Cache-Related Methods

**`Sis.write_cache(self): ...`**

If you do happen to initialize Sis yourself for some reason, this method can
be used to write the pickled class instance into the cache. You can then
reload that class instance elsewhere via `Sis.read_cache()`.

**`Sis.read_cache(cls, check_date=True) -> Sis: ...`**

This classmethod loads and returns a previous pickled instance of `Sis`
in the helper data directory. Uses a heuristic to try to remind you to update
things at the beginning of the school year by raising a ValueError if you're
using an instance cached in May/June during September/October.

**`Sis.cache_exists() -> bool: ...`**

This is a staticmethod.

## Entities

Several related entities are referenced throughout the module and can be used
for typing in your own code. I will refactor these to dataclasses one day,
and so I will document them as if they are dataclasses (they're not).

I also dislike that all of these fields can be None because it makes things
unnecessarily complex, but that's another thing I aim to fix some day.

```python
@dataclass
class Student:
    context.setdefault("groups", [])
    context.setdefault("guardians", [])
    first_name: str | None
    last_name: str | None
    student_id: str | None
    homeroom: str | None
    grade_level: str | None
    groups: str | None
    email: str | None
    guardians: list[ParentGuardian]
    self.primary_contact: ParentGuardian | None

    @property
    def name(self):
      return self.first_name + " " + self.last_name


@dataclass
class ParentGuardian:
    student: Student
    first_name: str | None
    last_name: str | None
    home_phone: str | None
    mobile_phone: str | None
    work_phone: str | None
    email: str | None
    relationship_to_student: str | None
    primary_contact: bool | None
    allow_contact: bool | None
    student_resides_with: bool | None

    @property
    def name(self):
      return self.first_name + " " + self.last_name


@dataclass
class Group:
    name: str | None
    grade_level: str | None
    students: list[Student]


class Homeroom:
    teacher: str
    grade_level: str
    students: list[Student]

```
