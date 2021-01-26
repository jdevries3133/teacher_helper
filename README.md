# Overview

This is a library of stuff that I have, used to automate
my work as a teacher. For the most part, it's been the primary means for me
learning object oriented programming, and has had a history of massive revision
as I continue to learn and fix my mistakes. There are currently three major
useful parts of this project:

1. <a href="#helper">teacherHelper</a>
2. <a href="#paychex">paychex</a>
3. <a href="#classroom-automator">pyautogc</a>

First, the Helper class encapsulates information that I deal with as a teacher.
This includes an object-oriented representation of teachers, students,
homerooms, parents, and extra-curricular groups.
The most important attribute is helper.students which is a dictionary; students'
full names are the keys, and Student class instances from `helper/student.py`
corresponding to that student are the values. Honestly, the Helper class is
really just your school's Student Information System, but in python. Look at
the classes helper.student.Student, helper.parent_guardian.ParentGuardian,
and helper.homeroom.Homeroom, and helper.group.Group. All of these classes
are nestled within the helper class so that you can compose loops and
make selections within python to find information on students. For example,

```python
>>> helper.students.get('Johnny Smith').homeroom.teacher
Jones
>>> all_fourth = [s for s in helper.students.values() if s.grade_level == 4]
>>> all_fourth
[<helper.student.Student object at 0x1032862b0>, ...]
>>> {s.homeroom for s in all_fourth}
{"Jones", "Smith", "Henderson", ...}
```

<h1 id="helper">Helper</h1>

> An object-oriented representation of teachers, students,
> homerooms, parents, and extra-curricular groups.

## Top-Level `shell.py`

On my machine, I call this utility through
[this wrapper script,](https://github.com/jdevries3133/my_shell_scripts/blob/master/emp)
although there are many ways to set it up for yourself. Putting that script
in your `PATH` is nice, though, because you only need to change one constant,
and then things should "just work."

Importantly, you first need to create a virtual environment for the project.
First, figure out the command for python <= version 3.8 on your machine;

- `python3 --version` or `python3.8 --version`; whatever returns python3.8
  or higher

Then, create the virtual environment and install dependencies

```bash
[python3|python3.8] -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Finally, instantiate the helper object and create a cache by calling
`helper.write_cache()`.
<a href="#helper">See here for details.</a>

### Usage

Once installed, shell.py provides the following utilities:

    Supported commands:

    student [name]
        Prints the student according to Student.__str__(). Provides basic
        student and guardian information.

    parent [parent/guardian name]
        Prints the student just like in student search, but search by
        parent instead of by student. Search algorithm prioritizes primary
        contacts; so a fuzzy string match with a primary contact at a
        lower confidence will be returned over a better match against a
        secondary contact.

    report [student name]
        Print a report for the student that includes zoom attendance
        record. A simple grep through `./data/zoom_attendance_reports`,
        presumed to be a directory of csv files.

    clock
        Automatically clocks in or out of Paychex, depending on time of day
        and previous clock state.

    timer [minutes] [message]
        Start a timer that will say [message] after [minutes]. The message
        will be spoken by a robot voice. Depends on osx `say` utility.

    new
        Will refresh the cache by loading in spreadsheets at
        `./data/students.csv` and `./data/parents.csv`.

    [no arguments]
        Run this script with no arguments, and it will enter the shell mode.
        Here, the helper object is instantiated in the local namespace with
        the variable name "helper".

<h2 id="helper-instantiation">Initial Instantiation</h2>

One of the most difficult things is first instantiation. The helper class gets
a new_school_year function from it's parent class, `OnCourseMixin`. This
method specifically works for me with the reports I can generate from OnCourse.

**`helper.new_school_year(cls, student_data, guardian_data, strict_headers=False)`**

Class method inherited from `helper/HelperMixins/oncourse/mixin.py`. The
student_data csv should have the following columns:

- first name
- last name
- grade level
- homeroom teacher
- email address
- birth date

The guardian_data csv should have the following columns:

- first name
- last name
- student
- primary contact
- email
- mobile phone
- home phone
- work phone
- comments
- allow contact
- student resides with
- relationship to student

These reports can be easily exported from OnCourse, and by passing them into
this function, the helper class will be instantiated.

If `strict_headers` is set to true, it will look for an exact match in the
header column. By default, it just uses an "if in" match. It's pretty wonky;
probably just leave that alone.

## Helper Class Methods

### find_nearest_match(self, student_name, auto_yes=False)

Takes a student name and returns a Student instances. Asks for the user input
to confirm the nearest match if no exact match is found. Set auto_yes to false,
and it will not ask for user input, it will simply go with the best match.

<h1 id="paychex">Paychex</h1>

```python
from paychex import Paychex
```

### Overview

Paychex class can clock in and out of paychex using headless Google Chrome,
selenium, and chromedriver.

### Automatic OTP-Fetching

```python
from paychex import PaychexOTP
```

Using the above import instead will include some automatic one time password
fetching functionality; but with a few setup steps.

- To allow the module to read your email:
  - Define `EMAIL_USERNAME` and `EMAIL_PASSWORD` as environment variables.
- So the module knows where to look:
  - Automatically forward all paychex one-time-passwords to an email folder
    named "Paychex."

Theoretically this version "just works," but I found that in reality it is
cumbersome and it takes a long time for the message to be forwarded from
your phone to your email to this program. In the future, I would like to
add twilio integration to make this progress seamless, but for now just
typing the one-time-password is probably easiest.

### Methods

**`self.clock(self)`**

This is the primary top-level function – the one that is called by passing
"clock" as a single argument to the shell. It takes into consideration the time
of day, cached clock state, and real site state, and makes a determination about
whether to press the button or not. It then updates the clock state and closes
the headless browser. It will be cautious and ask the user to confirm if they
are trying to clock out in the morning or clock in in the afternoon.

**`self.clock_in(self)`**

Clock in. The @login_first decorator is applied, so if you haven't done that yet,
it will happen upon calling this method.

This method does not mindlessly press the button in paychex. It first reads the
DOM and checks if you're already clocked in. It may push the button, or may just
close the borwser if you're already clocked in. Either way,
**you will be clocked in when all is said and done**

**`self.clock_out(self)`**

Same as clock in, but clock out.

<h1 id="classroom-automator">pyautogc</h1>

**The code is the documentation, good luck 😉**

`ClassroomAutomator` is the lowest base class with a lot of the selenium code
that actually navigates google classroom. The `FeedbackAutomatorBase` inherits
and extends `ClassroomAutomator` to give
feedback for google doc and slide based assignments in google classrooms,
which is quite tedious. However, this is an abstract class. A sample
implementation is the `FeedbackAutomator`, but it will be necessary to make
a new implementation for each assignment simply to define the comment
bank and assess method.
