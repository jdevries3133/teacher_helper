# Classroom API Wrapper

> ### Note!
>
> You will need to setup oauth credentials on the Google Cloud Platform and
> provide those credentials to this library before you can use this module.
> See documentation on the [client wrapper](./client.md) for directions.

<blockquote style="background-color: #fedada">
  <h3>Warning</h3>
  <p>
      This module does not have thorough unit tests yet. Please validate the
      results with care, report bugs that you find, and consider contributing some
      tests!
  </p>
</blockquote>

## Module `teacherhelper.google.classroom_wrapper`

Wrapper for the google classroom API, which also optionally makes calls to the
drive and slides API for certain methods, when credentials are provided.

### Class `classroom_wrapper.GoogleClassroomApiWrapper`

**`GoogleClassroomApiWrapper.__init__`**

Full Signature:

```python
def __init__(
    self,
    *,
    match_assignments: list[str] = None,
    match_classrooms: list[str] = None,
): ...
```

_match_assignments_ and _match_classrooms_ are lists of regex patterns that
filter the set of all possible assignments and classrooms that belong to you.
This allows you to easily iterate over assignment submissions across multiple
classroom or assignments simply by describing what you want when the class
is initialized. For example if you want to grade the assignment, "4/25 Homework"
in Ms. Smith and Ms. Fischer's homerooms, you might initialize the
GoogleClassroomApiWrapperClassroom like this:

```python
my_wrapper = GoogleClassroomApiWrapper(
    match_classrooms=['Ms. Smith', 'Ms. Fischer'],
    match_assignments=['4/25 Homework']
)
```

#### Automatic Traversal

The most appealing thing about this wrapper is that it can automatically
traverse assignment submissions across multiple classrooms or assignments.

**`GoogleClassroomApiWrapper.traverse_submissions(self) -> Generator[tuple[dict, dict, dict], None, None]: ...`**

Iteratively traverse all assignment submissions that match criteria provided on
initialization. Yields a tuple of the current course, assignment, and
submission.

Example usage:

```python
# see my_wrapper initialization example above

for classroom, assignment, submission in my_wrapper.traverse_submissions():
    # this will keep on generating submissions with context that match the
    # criteria
    assert classroom['name'] in ('Ms. Smith', 'Ms. Fischer')
    assert re.match('4/25 Homework', assignment['title']) is not None
    print(submission)
```

#### Convenience Methods

**`GoogleClassroomApiWrapper.download_file(self, file_id: str, mime_type): ...`**

Drive file ids are part of submission objects, so you can pass that id into
this method to export the whole file as any supported MIME type. See [supported
MIME types.](https://developers.google.com/drive/api/guides/mime-types)

ValueError will be raised if a google drive service object was not passed
at initialization time.

**`GoogleClassroomApiWrapper.get_student_profile(self, submission) -> dict: ...`**

Student names and other information is annoyingly not included in the
submission resource, so this method will trigger an additional request to get
that additional information.

**`GoogleClassroomApiWrapper.get_slides(self, submission, file) -> tuple[dict, dict]: ...`**

Returns a tuple of two slideshow representations: the teacher slide,
then the student slide.

ValueError will be raised if a google slides service object was not passed
at initialization time.

**`GoogleClassroomApiWrapper.get_content(self, submission, file, mime_type="text/plain") -> tuple[str, str]: ...`**

Like `get_slides`, this method returns a tuple of `(teacher_content, student_content)`. However, this is pure content; text content by default, but
it can be in the form of any MIME type that Drive supports. See [supported MIME
types.](https://developers.google.com/drive/api/guides/mime-types)

**`GoogleClassroomApiWrapper.find_parent_id(self, submission, file) -> str: ...`**

Returns the drive id of the "parent" file for a given student attachment. This
operates on the assumption that google classroom uses the naming convention
`<student name> - <original file name>` for student submissions. This method is
useful because it can lead you to the teacher's original file from which the
student is derived. This could be used, most simply, to check for completion
by checking for changes, or by rendering only the differences between the
teacher's original file and the student's submission.

#### Manual Traversal Methods

These methods are used for manually traversing classrooms, assignments, and
submissions.

**`GoogleClassroomApiWrapper.get_classrooms(self) -> list[dict]: ...`**

Return all the courses that match the _match_classrooms_ patterns provided
during initialization.

**`GoogleClassroomApiWrapper.get_assignments(self, course) -> list[dict]: ...`**

Return all the assignments in this course that match the _match_assignments_
patterns provided during initialization for the given course.

**`GoogleClassroomApiWrapper.get_submissions(self, assignment): list[dict]: ...`**

Return all the submissions for a given assignment
