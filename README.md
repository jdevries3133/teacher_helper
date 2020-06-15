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

### **init**(self, homerooms, students, groups)

Do not initialize this function through init unless you want to manaully make
homerooms, students, and groups. Use new_school_year to parse new data, or
read_cachs() if you've written data to the cache before.

### write_cache(self)

Write self to the cache as db['data']. This is run automatically after new_school_year
so that in the future, you can use the staticmethod read_cache() anytime. Re-run
write_cache() anytime data is out-of-date.

### get_regex_classroom_doc(self, doc_dir, regex, yes=False, bad_link_regex=r'')

Iterate through a list of word documents downloaded from google classroom.
The assumption is that docs will follow the naming convention where the student's
full name is the start of the filename, followed by a dash. Optionally, it can
also take a bad link regex which will pull out bad links, so that you can follow
up with students who pasted partial links. Returns a list of tuples of the
student name paired with the regex match string or None. If a `bad_link_regex` is
supplied, the function returns two list of tuples, first `matched_links`, then
`bad_links`.

### match_assgt_with_students(self, context)

Iterates through each homeroom and all google classroom json objects, and sets
the `assignments` attribute on each student; which is itself a list of
`AssignmentSubmission` objects (class defined in `sparta_helper/assignment_submissions.py`).

Importantly, this function needs quite a but of context to know where to look for
all this edpuzzle and flipgrid assignment information. Required keys for context
are:

- `flipgrid_assignments`
- `edpuzzle_assignments`
- `epoch_cutoff`

#### Flipgrid and Edpuzzle Assignments

Should point to a list of tuples:
`(ASSGT_NAME, CSV_PATH)`
The assignment name must exactly match the google classroom assignment name,
and the path should point to the csv file of data from flipgrid/edpuzzle so that
the data can be aggregated into the output of the function.

#### Epoch Cutoff

Assignments from before this timestamp will be ignored.

### write_assignments_to_workbook(self, output_path)

Once the above function has been run, all students will have an assignment
attribute. This function produces a report in excel with color-coded cells, which
is convenient for analyzing and transferring the data, such as for posting grades
or preparing progress reports.

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
accounts. This file is opened and new accounts are collated into the old. The result is written to `./soundtrap_updated.csv`

#### Sample

```
if __name__ == '__main__':
    path_in = Path.resolve(Path('.', 'soundtrap_in.csv'))
    path_out = Path.resolve(Path('.', 'soundtrap_out.csv'))
    path_update = Path.resolve(Path('.', 'soundtrap_update.csv'))

    helper = Helper.read_cache()
    students = helper.soundtrap_update(path_in, path_out, path_update, debug=False)
    input('Upload "soundtrap_out.csv to soundtrap now.')
    helper.email(students, 'soundtrap')
```

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
