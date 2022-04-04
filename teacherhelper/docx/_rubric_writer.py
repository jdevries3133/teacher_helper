"""The document writer can read the rubric template at ./rubric.docx and build
the output document of all student results, which will be returned to students."""

from copy import deepcopy
from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Sequence, Union, cast, Dict

from docx import Document
from docx.document import Document as DocumentType
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml

from teacherhelper.sis import Student
from .._data_dir import get_data_dir


logger = logging.getLogger(__name__)


@dataclass
class Page:
    student: Student
    rubric_grades: Dict[str, int]
    extra_rubric_fields: Union[Dict[str, str], None] = None
    notes: Union[str, None] = None


class RubricWriter:
    def __init__(
        self,
        *,
        template_doc: Union[Path, str, DocumentType],
        grade_to_col_mapping: Dict[int, int],
        cell_highlight_color: str = "CCCCCC",
    ):
        """*template_doc* is a path to your template. If you pass a string,
        it will be presumed to be relative to $HELPER_DATA.

        grade_to_col_mapping is a mapping between the grade and the
        corresponding rubric column, which is used during rubric cell shading.
        The right side of this mapping should be a zero-based index of a
        column in the table. Consider this example table:

        |               | 0           | 10          | 15          | 20          | total           |
        | ------------- | ----------- | ----------- | ----------- | ----------- | --------------- |
        | homework      | ...criteria | ...criteria | ...criteria | ...criteria | <homework>      |
        | classwork     | ...criteria | ...criteria | ...criteria | ...criteria | <classwork>     |
        | participation | ...criteria | ...criteria | ...criteria | ...criteria | <participation> |

        The correct mapping for this rubric would be:
            grade_to_col_mapping = {0: 1, 10: 2, 15: 3, 20: 4}

        *cell_highlight_color* can be any hex color code that you want to use
        for shading cells. By default, it's just gray.
        """

        if isinstance(template_doc, Path):
            self.doc = cast(DocumentType, Document(template_doc))
        elif isinstance(template_doc, str):
            # template_doc path is relative to teacherhelper data dir when a
            # string is passed
            self.doc = Document(get_data_dir() / template_doc)
        else:
            self.doc = template_doc

        self.cell_highlight_color = cell_highlight_color
        self.grade_to_col_mapping = grade_to_col_mapping

    def add_page(self, page: Page):
        """Sets page to self.current_page, then dispatches to page writing
        methods in the following order:

        1. _setup_page
        2. before_rubric
        3. add_rubric
        4. after_rubric
        """
        self.current_page = page
        self._setup_page()
        self.before_rubric()
        self._add_rubric()
        self.after_rubric()

    def add_pages(self, pages: Sequence[Page]):
        for page in pages:
            self.add_page(page)
            logger.debug("wrote page for %s", page.student.name)

    def _setup_page(self):
        """This is where we add the page break, so probably don't override me."""
        self.doc.add_page_break()

    def before_rubric(self):
        """Insert content on the page before the rubric"""
        self.doc.add_paragraph(f"Your Name: {self.current_page.student.name}")

    def after_rubric(self):
        """Insert content on the page after the rubric"""
        if self.current_page.notes is not None:
            self.doc.add_paragraph(f"Notes: {self.current_page.notes}")

    def _add_rubric(self):
        """Merge data from `Page` into the current page's rubric."""
        p = self.doc.add_paragraph()
        p._p.addnext(self._template_table)

        for target, value in self.current_page.rubric_grades.items():
            self._insert_grade(target, value)

        if self.current_page.extra_rubric_fields is not None:
            for target, value in self.current_page.extra_rubric_fields.items():
                self._replace_table_text(target, value)

    def _insert_grade(self, template_target: str, value: int):
        """Looks for the template target, enters the value as a string, but
        also looks up the value from self.grade_to_col_mapping to find which
        cell to shade, and shade that cell."""
        _, i_row, _ = self._replace_table_text(
            template_target, str(value), search_tables=[self.doc.tables[-1]]
        )
        i_cell = self.grade_to_col_mapping[value]
        cell = self.doc.tables[-1].rows[i_row].cells[i_cell]
        self._highlight_cell(cell)

    def _replace_table_text(self, search, replace: str, search_tables=None):
        """Returns the index of the table, row, and cell that the text was
        found in. If `search_tables` is specified, the returned table index
        refers to the passed-in list, not tables in the whole document."""
        if search_tables is None:
            search_tables = self.doc.tables
        for i, table in enumerate(search_tables):
            for j, row in enumerate(table.rows):
                for k, paragraph in enumerate(row.cells):
                    if search in paragraph.text:
                        # cursed, but this seems to replace the paragraph's
                        # inner text, preventing the formatting from being
                        # changed, and maintaining the text position formatting
                        # as being in the middle of the cell
                        paragraph.paragraphs[0].text = replace
                        return i, j, k

        raise Exception(f"could not perform replacement for {search}")

    def _highlight_cell(self, cell):
        shading_elm_1 = parse_xml(
            r'<w:shd {nsdecl} w:fill="{color}"/>'.format(
                nsdecl=nsdecls("w"), color=self.cell_highlight_color
            )
        )
        cell._tc.get_or_add_tcPr().append(shading_elm_1)

    @property
    def _template_table(self):
        return deepcopy(self.doc.tables[0]._tbl)
