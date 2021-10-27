# Core Data

The core of this library is the data that you put into it. Once it is setup,
this library becomes glue that allows you to put together scripts which
can easily consume and interpret data having to do with your school.

## `$HELPER_DATA` and the Data Directory

The library needs a file store to consume student data that you provide,
maintain an object cache, and locate your html email templates. By default,
this location is `~/.teacherhelper`, a hidden folder in your home directory.

If you prefer, you can change the location of this folder by setting the
`HELPER_DATA` environment variable to be a path to any existing folder on your
system that you would like the library to use.

## Initial Setup via `th --new`

The module will work with data in one directory of your machine. You should
define the path to this directory as an environment variable: `HELPER_DATA`.

In that folder, you should put two `csv` files that contain the data you want
to populate the module with: `students.csv` and `guardians.csv`.

`students.csv` should contain the following exact columns:

- `first name`
- `last name`
- `grade level`
- `homeroom teacher`
- `email address 1`
- `birth date`

`guardians.csv` should contain the following exact columns:

- `guardian first name`
- `guardian last name`
- `student first name`
- `student last name`
- `primary contact`
- `guardian email address 1`
- `guardian mobile phone`
- `guardian phone`
- `guardian work phone`
- `comments`
- `allow contact`
- `student resides with`
- `relation to student`
