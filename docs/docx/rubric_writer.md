# Rubric Writer

The rubric writer is focused on specifically filling out rubrics.
[python-docx,](https://python-docx.readthedocs.io/en/latest/) which provides
the underlying functionality. Use of this module also requires you to reach
down into the python-docx api for certain things, but the RubricWriter will
help you if you have a typical rubric represented as a table. It take a
template document, replace text targets inside the table, copy the table across
multiple pages as it merges data in, and also shade in table cells.

Since the RubricWriter is focused on handling rubrics (tables) only, there are
methods you can easily override to extend its functionality for your use case.

You will need to build a template document that this class can copy from and
build on. The template should have a table (the actual rubric), and the rubric
should have some template text which will be a target for replacement whenever
you add a page. **An example template is included with this library,** mainly
for testing purposes, but you can also use it as a starting point for building
your own rubrics that are suitable for this module. [Click here to see the
example rubric](https://github.com/jdevries3133/teacher_helper/blob/3229c31a5bf15494a74709e4a2ea7c201513789a/teacherhelper/docx/tests/assets/sample_rubric.docx)

Here is some sample usage which demonstrates how you would use the RubricWriter
with that a hypothetical example template.

```python
from pathlib import Path

from teacherhelper.docx import RubricWriter, Page
from teacherhelper.sis import Student

pages = [
    Page(
        student=Student({'first_name': 'Tim', 'last_name': 'Smith'}),
        rubric_grades={'<week 19>': 10, '<week 20>': 15, '<week 21>': 20},
        extra_rubric_fields={'total': 10 + 15 + 20 + 40},
        notes="Nice work tim!"
    ),
    Page(
        student=Student({'first_name': 'Jane', 'last_name': 'Jones'}),
        rubric_grades={'<week 19>': 0, '<week 20>': 10, '<week 21>': 0},
        extra_rubric_fields={'total': 0 + 10 + 0 + 40},
        notes="Better luck next time, Jane..."
    )
]

path_to_template = Path('example_rubric.docx')

writer = RubricWriter(
    template_doc=path_to_template,

    # see below for an explanation of this
    grade_to_col_mapping={0: 1, 10: 2, 15: 3, 20: 4},
)

writer.add_pages(pages)
writer.doc.save('output.docx')
```

## class `teacherhelper.docx.RubricWriter`

### Attributes

**`RubricWriter.doc: docx.document.Document`**

The _doc_ attribute allows you to access the underlying document. This is
necessary for eventually saving the document that you generate as a file.

**`RubricWriter.current_page: Page`**

If you override the _before_rubric_ or _after_rubric_ methods, this is how
you should get the current page.

### Methods

**`RubricWriter.__init__(...): ...`**

Full signature:

```python
def __init__(
    self,
    *,
    template_doc: Union[Path, str, docx.document.Document],
    grade_to_col_mapping: Dict[int, int],
    cell_highlight_color: str = "CCCCCC",
): ...
```

_template_doc_ is a path to your template. If you pass a string,
it will be presumed to be relative to $HELPER_DATA. It can also be an instance
of python-docx's Document class, in which case it will be directly used and
appended to.

grade_to_col_mapping is a mapping between the grade and the
corresponding rubric column, which is used during rubric cell shading.
The right side of this mapping should be a zero-based index of a
column in the table. Consider this example rubric:

|               | 0           | 10          | 15          | 20          | total            |
| ------------- | ----------- | ----------- | ----------- | ----------- | ---------------- |
| homework      | ...criteria | ...criteria | ...criteria | ...criteria | <homework\>      |
| classwork     | ...criteria | ...criteria | ...criteria | ...criteria | <classwork\>     |
| participation | ...criteria | ...criteria | ...criteria | ...criteria | <participation\> |

The correct mapping for this rubric would be:

```python
{0: 1, 10: 2, 15: 3, 20: 4}
```

_cell_highlight_color_ can be any hex color code that you want to use
for shading cells. By default, it's just gray.

**`RubricWriter.add_page(self, page: Page): ...`**

Sets page to _self.current_page_, then dispatches to page writing
methods in the following order:

1. `RubricWriter._setup_page`
2. `RubricWriter.before_rubric`
3. `RubricWriter._add_rubric`
4. `RubricWriter.after_rubric`

Don't override me! Override one of the dispatch targets in that list instead.

**`RubricWriter.add_pages(self, pages: Sequence[Page]): ...`**

Plural form of the above.

**`RubricWriter.before_rubric(self): ...`**

This is a good method to extend or override. Use _self.current_page_ to refer
to the current page if you write a different implementation.

Default behavior is to write a paragraph with the current student's
name.

**`RubricWriter.after_rubric(self): ...`**

This is a good method to extend or override. Use _self.current_page_ to refer
to the current page if you write a different implementation.

Default behavior is to write the page's notes at the bottom of the page.
