from pathlib import Path

import os
import pytest

from teacherhelper.sis import Student
from .._rubric_writer import RubricWriter, Page


@pytest.fixture
def writer():
    return RubricWriter(
        template_doc=Path(Path(__file__).parent, "assets", "sample_rubric.docx"),
        grade_to_col_mapping={0: 1, 10: 2, 15: 3, 20: 4},
    )


@pytest.fixture
def guido():
    return Student({"first_name": "Guido", "last_name": "VanMorrison"})


@pytest.fixture
def timmy():
    return Student({"first_name": "Tim", "last_name": "Peters"})


@pytest.fixture
def joey():
    return Student({"first_name": "Joey", "last_name": "Jones"})


def test_add_page(writer, joey):
    writer.add_page(
        Page(
            student=joey,
            rubric_grades={"<week 19>": 10, "<week 20>": 15, "<week 21>": 0},
        )
    )

    # a table was added
    assert len(writer.doc.tables) == 2
    assert f"Your Name: {joey.name}" in [p.text for p in writer.doc.paragraphs]
    assert writer.doc.tables[1].rows[1].cells[-1].paragraphs[0].text == "10"
    assert writer.doc.tables[1].rows[2].cells[-1].paragraphs[0].text == "15"
    assert writer.doc.tables[1].rows[3].cells[-1].paragraphs[0].text == "0"


def test_page_with_notes(writer, timmy):
    writer.add_page(
        Page(
            student=timmy,
            rubric_grades={"<week 19>": 10, "<week 20>": 15, "<week 21>": 0},
            notes="You can do better than that, tim",
        )
    )
    assert (
        writer.doc.paragraphs[-1].text
        == "Notes: You can do better than that, tim"
        in [p.text for p in writer.doc.paragraphs]
    )


def test_add_pages(writer, joey, guido, timmy):
    writer.add_pages(
        [
            Page(
                student=joey,
                rubric_grades={"<week 19>": 10, "<week 20>": 15, "<week 21>": 0},
            ),
            Page(
                student=timmy,
                rubric_grades={"<week 19>": 10, "<week 20>": 15, "<week 21>": 0},
            ),
            Page(
                student=guido,
                rubric_grades={"<week 19>": 10, "<week 20>": 15, "<week 21>": 0},
            ),
        ]
    )

    assert len(writer.doc.tables) == 4
    # spot check data
    assert writer.doc.tables[1].rows[1].cells[-1].text == "10"
