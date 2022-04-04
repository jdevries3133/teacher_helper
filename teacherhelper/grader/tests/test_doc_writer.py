from pathlib import Path

import pytest

from .._entities import Student
from ..doc_writer import Term2DocWriter, Page


@pytest.fixture
def writer():
    return Term2DocWriter(Path(Path(__file__).parent, "assets", "sample_rubric.docx"))


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
    writer.add_page(Page(student=joey, wk_19_grade=10, wk_20_grade=15, wk_21_grade=0))

    # a table was added
    assert len(writer.doc.tables) == 2
    assert writer.doc.paragraphs[7].text == f"Name: {joey.name}"
    assert writer.doc.tables[1].rows[1].cells[-1].paragraphs[0].text == "10"
    assert writer.doc.tables[1].rows[2].cells[-1].paragraphs[0].text == "15"
    assert writer.doc.tables[1].rows[3].cells[-1].paragraphs[0].text == "0"


def test_page_with_notes(writer, timmy):
    writer.add_page(
        Page(
            student=timmy,
            wk_19_grade=10,
            wk_20_grade=15,
            wk_21_grade=15,
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
            Page(student=joey, wk_19_grade=10, wk_20_grade=15, wk_21_grade=0),
            Page(student=timmy, wk_19_grade=10, wk_20_grade=20, wk_21_grade=0),
            Page(student=guido, wk_19_grade=15, wk_20_grade=20, wk_21_grade=15),
        ]
    )

    assert len(writer.doc.tables) == 4
    # spot check data
    assert writer.doc.tables[1].rows[1].cells[-1].text == "10"
