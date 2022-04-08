<!-- NOTE: there is a symlink, so this is *both* /README.md and /docs/index.md.
           don't use mkdocs-specific stuff, or github-specifc stuff in here,
           because it will break somewhere -->

[![Teacher Helper CI/CD](https://github.com/jdevries3133/teacher_helper/actions/workflows/ci_cd.yml/badge.svg)](https://github.com/jdevries3133/teacher_helper/actions/workflows/ci_cd.yml)

# Overview

This is a library of stuff that I have used to automate my work as a teacher.
With version 2.0, I've worked to increase the quality of the codebase by adding
unit tests, comitting to API stability (see
[contributing](https://teacherhelper.jackdevries.com/contributing#versioning)),
creating this documentation site, and creating a CI/CD pipeline. My hope is
that these efforts make this codebase useful to others, and that others might
even consider contributing!

## Installation

You can install this package via pip:

```bash
pip install teacherhelper
```

Then, perform the setup described in
[setup instructions.](https://teacherhelper.jackdevries.com/setup/)

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

## Example Usage

```python

name = 'tommey'  # Timmy needs a typing lesson, but this library is great for
                 # data bunging!

# **************************************************
# ==== Student Information System inside Python ====
# **************************************************

from teacherhelper.sis import Sis

# some assembly required! Docs site link is at the end of the README
helper = Sis.read_cache()

# name is matched by fuzzy search, match threshold is adjustable with a kwarg
result: Student | None = helper.find_student(name, threshold=80)
if result:
    print(result)
else:
    print(f'{name} not found')

parent = 'Lisa Tommymom'
parent = sis.find_parent(name)
if parent:
    print(f'{parent.name=} :: {parent.phone_number=}')


# **************************************************
# ==== Traverse Google Classroom ====
# **************************************************

from teacherhelper.google_classroom import GoogleClassroomApiWrapper

# again, setup steps are documented on the docs site
wrapper = google_classroom.GoogleClassroomApiWrapper(
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

# you can also define EMAIL_USER and EMAIL_PASSWORD environment variables
with Email(username="me@example.com", password="supersecret") as eml:
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
""",
        cc=result.email
    )
```

## Documentation Site

Visit the documentation site at [teacherhelper.jackdevries.com](https://teacherhelper.jackdevries.com/)

### About the Docs Site

The docs site will _always_ remain in sync with the latest release. Every
release is tagged on GitHub, so use version control to access documentation for
previous versions.
