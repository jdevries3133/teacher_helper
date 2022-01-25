# Setup

The core of this library is the data that you put into it. After setup, you
will have a simple and expressive Object-Oriented Python API for interacting
with students, homerooms (course sections), grade levels, etc.

## `$HELPER_DATA` and the Data Directory

The library needs storage to consume student data that you provide, maintain an
cache for fast startup, and locate your html email templates if you provide
any. By default, this location is `~/.teacherhelper`.

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

## Usage After Setup

After running `th --new`, the module is initialized, and you'll notice a binary
cache will have been written to the data directory (`~/.teacherhelper`, by
default). The CLI will now work. Additionally, you can use the Python API
[as shown in the readme.](../README.md)

Note that the `helper` object should always be initialized with the `read_cache()`
method.

# Maintainance

Students add and drop all the time. To keep your cache in sync, export new
`csv` files from your learning management system, place them into the
correct location as described in [initial setup.](#initial-setup-via-th---new)
Then, just run `th --new` again. Depending on the capibilities of your LMS,
this may or may not be easily automatable with a cron job.
