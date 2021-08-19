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

Once installed, the `th` command provides the following CLI utilities:

    Supported commands:

    --student -s [name]
        Prints the student according to Student.__str__(). Provides basic
        student and guardian information.

    --parent -p [parent/guardian name]
        Prints the student just like in student search, but search by
        parent instead of by student. Search algorithm prioritizes primary
        contacts; so a fuzzy string match with a primary contact at a
        lower confidence will be returned over a better match against a
        secondary contact.

    --new
        Will refresh the cache by loading in spreadsheets at
        `./data/students.csv` and `./data/parents.csv`.

    [no arguments]
        Run this script with no arguments, and it will enter the shell mode.
        Here, the helper object is instantiated in the local namespace with
        the variable name "helper".

## Initial Setup

The module will work with data in one directory of your machine. You should
define the path to this directory as an environment variable: `HELPER_DATA`.

In that folder, you should put two `csv` files that contain the data you want
to populate the module with: `students.csv` and `parents.csv`.

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

## Helper Class Methods

**`find_nearest_match(self, student_name) -> Student | None`**

Lookup a student.

**`find_parent(self, parent_name) -> Student | None`**

Lookup a student by parent name.

**`exhaustive_search(self, name, subgroup: list[Student], threshold: int)`**

Search for a student within a subgroup. This helps for dealing with data that
is gnarly, misspelled, or incomplete. If you know that you are processing
data from some subgroup of students like a single homeroom, you can add
that as a search parameter and also lower the confidence threshold, making
it possible to get more matches:

```python
name = 'Tomme'  # Tommy needs a typing lesson
subgroup = helper.homerooms['Smith']
tommy_object = helper.exhaustive_search(name, subgroup, threshold=50)
```
