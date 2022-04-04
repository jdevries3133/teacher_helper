# Overview

This is a library of stuff that I have, used to automate my work as a teacher.
For the most part, it's been the primary means for me learning object oriented
programming, and has had a history of massive revision as I continue to learn
and fix my mistakes. Most recently, in late summer 2021, I deleted most of the
project except the parts I actually use, and I plan to continue adding to it
throughout this school year; hopefully adding some things that are actually
useful!

## Installation

You can install this package via pip:

```bash
pip install teacherhelper
```

Of course, there is some additional work involved in importing your school
data. See [setup instructions.](https://teacherhelper.jackdevries.com/setup/)

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

## Student Information System (SIS)

The `Helper` object provides an object oriented interface for accessing
the imported data as well as sending emails if the optional `EMAIL_USERNAME`
and `EMAIL_PASSWORD` environment variables are set. This makes any kind of
scripting involving school information much more accessible.

```python

name = 'tommey'  # Timmy needs a typing lesson, but this library is great for
                 # data bunging!

# **************************************************
# ==== Student Information System inside Python ====
# **************************************************

from teacherhelper.sis import Sis

# after following the setup steps in ./docs/CORE.md, this "just works," making
# it super easy to interact with student information from any python script
helper = Sis.read_cache()

result: Student | None = helper.find_student(name)
if result:
    print(result)
else:
    print(f'{name} not found')

parent = 'Lisa Tommymom'
parent = helper.find_parent(name)
if parent:
    print(f'{parent.name=} :: {parent.phone_number=}')


# **************************************************
# ==== Traverse Google Classroom ====
# **************************************************

from teacherhelper.google_classroom import GoogleClassroomApiWrapper
from teacherhelper.google_client import get_service

wrapper = google_classroom.GoogleClassroomApiWrapper(
    {'classroom': get_service('classroom', 'v1')},
    match_classrooms=['Ms. Smith', 'Ms. Fischer'],
    match_assignments=['4/25 Homework']
)

for classroom, assignment, submission in my_wrapper.traverse_submissions():
    # this will keep on generating submissions that match the match criteria
    # described above
    assert classroom['name'] in ('Ms. Smith', 'Ms. Fischer')
    assert re.match('4/25 Homework', assignment['title']) is not None
    print(submission)


# **************************************************
# ==== Send Emails Easily ====
# **************************************************

from teacherhelper import Email

# don't forget our variables defined above
tommy = result

with Email(username="me@site.com", password="supersecret") as eml:
    eml.send(
        to=tommy.primary_conteact.email,
        subject="Tommy Needs Spelling Help",

        # the emailer supports markdown input, and will inject the resulting
        # html into a default template, or a template that you can create!
        message=f"""Hello Ms. {tommy.primary_contact.name},

I noticed that {tommy.first_name} spelled his name like "tommey" on an
assignment recently. Here are some spelling tools I would recommend:

## List of Spelling Tools

| Name                      | Website                          |
| ------------------------- | -------------------------------- |
| Khan Academy              | https://www.khanacademy.org/     |
| Grammarly                 | https://www.grammarly.com/       |
| Webster Dictionary Online | https://www.merriam-webster.com/ |
"""
        cc=result.email
    )
```

## Documentation Site

Visit the documentation site at [teacherhelper.jackdevries.com](https://teacherhelper.jackdevries.com/)