# Helper.do_stuff

## Top-Level `shell.py`

The idea is to alias this file to something easy to remember on your machine.
It exposes some of the module's functionality as a command line utility. Note
that you will need to update the shebang on the first line to point to the
correct interpreter on your machine.

### Setup Tutorial (OS X or Linux)

1. Allow `shell.py` to be executed directly.

   `chmod +x shell.py`

2. Add a convenient alias to `shell.py` in your ~/.bashrc file.

   `echo "export [your alias name]="path/to/`shell.py`" >> ~/.bashrc`

3. Instantiate the Helper class and call the `write_cache()` method. This cache will be used for shell utilities. See <a href="#helper">helper section</a> for details on instantiaiton.

### Utilities

`python shell.py student [name] (-v)`

Pretty prints the dictionary of the matching student. If verbose, also
print the dict of the students' guardians.

`python shell.py clock`
Automatically clocks in or out of Paychex, depending on time of day
and previous clock state.

`python shell.py` (no arguments)
Run this script with no arguments, and it will enter the shell mode.
Here, the helper object is instantiated in the local namespace with
the variable name "helper". All attributes and methods are accessible.

   <h1 id="helper">from helper import Helper</h1>

A class that encapsulates homerooms, students, extracurricular groups, and parent contacts.

### helper.new_school_year(cls, student_data, guardian_data)

Class method inherited from `helper/HelperMixins/oncourse_mixin.py`. The student_data csv should have the following columns in the following order:

- first name
- last name
- grade level
- homeroom
- email

The guardian_data csv should have the following columns in the following order:

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

These reports can be easily exported from OnCourse, and by passing them into this function, the helper class will be fully instantiated.

## Helper Class Methods

### find_nearest_match(self, student_names)

Takes a list of student names and returns a list of Student instances which
are a part of self.students(). Asks for the user's help in the command line unless
a single perfect match is found. Manipulations to these students will cascade.

<br />

# Paychex

## from helper.paychex import Paychex

### Overview

Paychex class can clock in and out of paychex. `__init__` takes two positional
arguments; `username`, and `password`.

### Methods

**`self.clock()`**

This is the primary top-level function – the one that is called by passing
"clock" as a single argument to the shell. It takes into consideration the time
of day, cached clock state, and real site state, and makes a determination about
whether to press the button or not. It then updates the clock state and closes
the headless browser.

**`self.login()`**

Launch headless chrome and login to paychex. Unless you setup the Imap module
to get your OTP from your email, you will have to input it.

**`self.clock_in()`**

Clock in. The @login_first decorator is applied, so if you haven't done that yet,
it will happen upon calling this method.

This method does not mindlessly press the button in paychex. It first reads the
DOM and checks if you're already clocked in. It may push the button, or may just
close the borwser if you're already clocked in. Either way,
**you will be clocked in when all is said and done**

**`self.clock_out()`**

Same as clock in, but clock out.

**`self.get_clock_state()`**

This returns the **LOCALLY CACHED** clock state. Can be used to check whether
the Browser should be opened.

**`self.set_clock_state()`**

This opens the browser, logs in, and gets the clock state from the website.
It does not take any arguments, or allow the state to by manually overridden.

**`@login_first decorator`**

These methods will check whether `self.is_logged_in` is true.
