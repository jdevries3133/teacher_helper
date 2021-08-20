# Overview

This is a library of stuff that I have, used to automate
my work as a teacher. For the most part, it's been the primary means for me
learning object oriented programming, and has had a history of massive revision
as I continue to learn and fix my mistakes. Most recently, in late summer
2021, I deleted most of the project except the parts I actually use, and I
plan to continue adding to it throughout this school year; hopefully adding
some things that are actually useful!

## Installation

You can install this package via pip:

```bash
pip install teacherhelper
```

## Usage

Once installed, the `th` command provides the following CLI utility:

```
usage: th [-h] [--student STUDENT] [--parent PARENT] [--new]

optional arguments:
  -h, --help            show this help message and exit
  --student STUDENT, -s STUDENT
                        Lookup a student and print the result
  --parent PARENT, -p PARENT
                        Lookup a parent and print the result
  --new                 Regenerate the database by parsing student.csv and parent.csv in the $HELPER_DATA directory.
```

## API

The `Helper` object provides an object oriented interface for accessing
the imported data as well as sending emails if the optional `EMAIL_USERNAME`
and `EMAIL_PASSWORD` environment variables are set. This makes any kind of
scripting involving school information much more accessible.

```python
import teacherhelper

name = 'tommey'  # Timmy needs a typing lesson

# the classmethod read_cache instantiates the helper object with all the
# data previously imported and cached with `th --new`.
helper = teacherhelper.Helper.read_cache()

result = helper.find_nearest_match(name)  # returns Student | None
if result:
    print(result)
else:
    print(f'{name} not found')

# there is also an `exhaustive_search` method which allows you to search within
# subgroups of students at a lower confidence level, allowing dirtier data to
# be more usable if you know that you are looking at a particular homeroom,
# for example
name = 'toezmmy'  # come on Tommy
tommy_homeroom = helper.homerooms["Tommy's Teacher"].students
result = helper.exhaustive_search(name, tommy_homeroom, threshold=40)
if result:
    print(result)
else:
    print(f'{name} not found')

# finally, Helper has a find_parent function, which returns a *student*
# by searching for the parent's name
parent = 'Lisa Tommymom'
result = helper.find_parent(name)
if result:
    # the method still returns a student object! This is usually what you want
    assert isinstance(result, teacherhelper.entities.Student)

    # you can still refer back to the parent from the student
    parent_name = result.primary_contact.name
    parent_email = result.primary_contact.email
```

### Extensive Documentation

There is no formal documentation besides this README. After my latest late
summer razing of the not-so-useful parts of the library, pretty little is
left! Please [review the source code on GitHub
](https://github.com/jdevries3133/teacherhelper) to learn more.

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
