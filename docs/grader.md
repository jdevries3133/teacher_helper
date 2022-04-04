# Grader

`teacherhelper.grader` contains tools to help automate grading tasks. This
module was derived from my
[term 2 grading project,](https://github.com/jdevries3133/term_2_grades)
and some components of it still only make sense in that context. However,
the generally useful components, as well as any caveats needed to make them
generally useful, are documented here.

## Module `teacherhelper.grader.google_classroom`

Wrapper for the google classroom API, which also optionally makes calls to the
drive and slides API.

### Class `google_classroom.GoogleClassroomApiWrapper`

**`GoogleClassroomApiWrapper.__init__`**

Full Signature:

```python
def __init__(
    self,
    services: dict[Literal['classroom', 'drive', 'slides'], Any],
    *,
    match_assignments: list[str] = None,
    match_classrooms: list[str] = None,
): ...
```

The value for objects in the _services_ dict should be Google python client
API service objects. Drive and slides objects are optional, and if they are
later called on without being provided, a ValueError will be raised. The
classroom service object is of course required and a ValueError will be raised
by `__init__` if it isn't provided.

_match_assignments_ and _match_classrooms_ are lists of regex patterns that
filter the set of all possible assignments and classrooms that belong to you.
This allows you to easily iterate over assignment submissions across multiple
classroom or assignments simply by describing what you want when the class
is initialized. For example if you want to grade the assignment, "4/25 Homework"
in Ms. Smith and Ms. Fischer's homerooms, you might initialize the
GoogleClassroomApiWrapperClassroom like this:

```python
my_wrapper = GoogleClassroomApiWrapper(
    {'classroom': google_classroom.get_service('classroom', 'v1')},
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

## Module `teacherhelper.grader.google_client`

This wraps google's python oauth client libraries, but uses `$HELPER_DATA` for
reading your credentials and storing your authentication token. To use this
module or it's dependencies (`teacherhelper.grader.google_classroom`), you
will need to generate Ouath credentials on the Google Cloud Platform. See
[Using OAuth 2.0 to Access Google APIs](https://developers.google.com/identity/protocols/oauth2)

After you get Oauth client credentials, put the `credentials.json` file in
`$HELPER_DATA/google_oauth/credentials.json`. For more about the helper data
dir, see [setup.](../setup) The google client module will also store the
Oauth token in `$HELPER_DATA/google_oauth/token.json`, so that you only
need to login the first time.

You need to make sure that your Oauth token at least supports the following
scopes, as well as any others that you wish to use:

```
openid
https://www.googleapis.com/auth/userinfo.email
https://www.googleapis.com/auth/userinfo.profile
https://www.googleapis.com/auth/presentations.readonly
https://www.googleapis.com/auth/classroom.courses.readonly
https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly
https://www.googleapis.com/auth/classroom.student-submissions.students.readonly
https://www.googleapis.com/auth/classroom.rosters.readonly
https://www.googleapis.com/auth/classroom.profile.photos
https://www.googleapis.com/auth/drive.readonly
```

The client wrapper will use the authentication scopes defined in
`google_client.ClientWrapper.DEFAULT_SCOPES`, which are the same as the ones
documented in the previous section. These default scopes are used by the main
ClientWrapper class, and also by the convenience functions, `get_service` and
`get_credentials`.

**`google_client.get_service(service: str, version: str)`**

Get one of the Google python client's service objects. These objects store
your authentication context, and can be used to interact with various Google
services.

### Convenience Functions

**`google_client.get_credentials()`**

Return the raw credentials object. This can be useful if you're using the
google account to authenticate with a third party service via an Oauth client
token. For example, I used this to access grades I had input on my [Fast
Grader Website](https://classfast.app/).

### `google_client.ClientWrapper`

Main client wrapper class.

**`ClientWrapper.BASE_DIR: Path`**

Path to `$HELPER_DATA/google_oauth`

**`ClientWrapper.CREDENTIALS` and `ClientWrapper.TOKEN`**

Path to `$HELPER_DATA/google_oauth/credentials.json` and
`$HELPER_DATA/google_oauth/token.json, respectively`

**`ClientWrapper.get_credentials(self): google.oauth2.credentials.Credentials`**

Method to fetch credentials, first checking for a valid cached token.

**`ClientWrapper.get_service(self, service: str, version: str)`**

Method to create a google client service object

