# Setup

The core of this library is the data that you put into it. After setup, you
will have a simple and expressive Object-Oriented Python API for interacting
with students, homerooms, grade levels, etc. This library also contains modules
for sending emails, interacting with Google Classroom, and generating rubrics.

## `$HELPER_DATA` and the Data Directory

The library needs storage to consume student data that you provide, maintain a
cache for fast startup, and locate your html email templates if you provide
any. By default, this location is `~/.teacherhelper`.

If you prefer, you can change the location of this folder by setting the
`HELPER_DATA` environment variable to be a path to any existing folder on your
system that you would like the library to use.

## Initial Setup via `th --new`

In the base of the data directory (described above), put two csv files that
contain the data you want to populate the module with: `students.csv` and
`parents.csv`.

`students.csv` should contain the following exact columns:

- `first name`
- `last name`
- `grade level`
- `homeroom teacher`
- `email address 1`
- `birth date`

`parents.csv` should contain the following exact columns:

- `guardian first name`
- `guardian last name`
- `student first name`
- `student last name`
- `primary contact` (boolean)
- `guardian email address 1`
- `guardian mobile phone`
- `guardian phone`
- `guardian work phone`
- `comments`
- `allow contact` (boolean)
- `student resides with` (boolean)
- `relation to student`

Boolean fields must be a literal `Y` or `N` or a `ValueError` will be raised.

Under the hood, this calls the `Sis.new_school_year` classmethod. It reads data
from the spreadsheet, constructs the necessary [entities](./sis.md#entities),
and calls [`Sis.write_cache`](./sis.md#cache-related-methods) to save the result.
This method isn't documented in detail, so [take a look at the source.](https://github.com/jdevries3133/teacher_helper/blob/main/teacherhelper/sis/_oncourse_mixin.py)

## Usage After Setup

After running `th --new`, the module is initialized, and you'll notice a cache
will have been written to the data directory ([as described
above](#helper_data-and-the-data-directory)). The CLI will now work.
Additionally, you can use the Python API [as shown in the readme.](./index.md)

Note that `sis.Sis` can thereafter be initialized by your python programs with
the [`read_cache`](./sis.md#cache-related-methods) method.

# Google Oauth Client

See [google client](./google/client.md#setup) for setup instructions.
