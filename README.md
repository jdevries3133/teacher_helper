# Helper.do_stuff
## Helper.new_school_year()
### Naming convention for source data
Source data must be named in a specific way. A filename should consist of three
specific parts:
```
[flag (-h or -g)] [grade level] [name (of teacher or group)]
```
For example,
```
-h3Masterson.csv
```
A "-h" and "-g" flags tells the program to parse students as homerooms or groups,
respectively. Homerooms have more academic-related methods, like automatically
following up on missing grades, whereas groups should be used for extracurricular
or sports groups. They include methods appropriate to those cases.

The csv for groups must contain a header row `name` to parse student names. Homerooms
should also have the header row `id`. The module automatically tries to match
group students with their matching homeroom instance, and to merge them. There
are various duplicate reconciliation functions, but they should be merged into
a single function executed during new_school_year instantiation. 

# Methods of the Helper function
## Regular Methods
### __init__(self, homerooms, students, groups)
Do not initialize this function through init unless you want to manaully make
homerooms, students, and groups. Use new_school_year to parse new data, or
read_cachs() if you've written data to the cache before.
### write_cache(self)
Write self to the cache as db['data']. This is run automatically after new_school_year
so that in the future, you can use the staticmethod read_cache() anytime. Re-run
write_cache() anytime data is out-of-date.

### read_emails_from_csv(self)
Depricated method that can assign a csv of names and emails to students. This
is from before read_cache() was working properly, but maybe still helpeful in
some instances.

### find_nearest_match(self, student_names)
Takes a list of student names and returns a list of Student instances which
are a part of self.students(). Asks for the user's help in the command line unless
a single perfect match is found. Manipulations to these students will cascade.

### resolve_missing_st_ids(self)
Iterate through students who have no student ID. Perform a fuzzy match on the
pool of students, and ask the user if it is a match. No-ID case often arises if
a group list is imported with nicknames. Often, student ID's are critical for
LMS endpoints.

For now, if the user says "n," the student is just deleted. Obviously the
assumption is that students who are not part of the school are not in any groups.
This function must be modified to handle students who are group members that are
not students in the school.

### find_non_participators(self, directories)
Current configured for google classroom, flipgrid, and edpuzzle; this module
works through the exported data from each of these programs and identifies whether
students have submitted that assignment. It then produces a color-coded report
in as an excel file. Helpful for finding chronic non-participators in online
learning to follow up. Still under progress.

### email_students(self, students, template_flag)
Emails `students` with one of the templates in `spart_helper.templates`. This
module uses gui automation, so gmail must be open in fullscreen, and it may not
work for all screen resolutions; however, it mostly uses keyboard shortcuts.

### soundtrap_update(input_path, output_path, update_path)
Students are constantly signing up for soundtrap accounts. Takes csv data from
google classroom at `input_path`, and writes a csv file to `output_path` which
can be uploaded to soundtrap. At `update_path` is a csv of all existing soundtrap
accounts. This file is opened and overwritten, collating the new accounts into
the old ones.

## Class Methods
### new_school_year(cls, csvdir)
See documentation at the top of this file.

## Static Methods
### get_matching_student(st, students, append_homeroom)
Depricated method replaced by find_nearest_match.

### read_cache(check_date=True)
Returns the most recent instance of the helper class. Once everything is straightened
out at the beginning of the year, this is the best way to instantitate the helper
class for normal routines. It includes error handling to detect caches that appear
to be from the incorrect school year. Behavior can be overwritten with the optional
argument check_date=False.