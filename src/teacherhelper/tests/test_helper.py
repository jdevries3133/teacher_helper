import csv
from typing import cast
import pytest
from shutil import rmtree
import shelve
import datetime
from tempfile import mkdtemp
from pathlib import Path

from .._data_dir import get_data_dir
from .fixtures import students_csv, parents_csv
from ..helper import Helper


@pytest.fixture
def helper(monkeypatch, students_csv, parents_csv):
    """This ultimately calls into the OnCourseMixin to create a new populated
    helper object."""
    dir = Path(mkdtemp())
    monkeypatch.setenv("HELPER_DATA", str(dir))
    for filename, data in (
        ("students.csv", students_csv),
        ("parents.csv", parents_csv),
    ):
        with open(dir / filename, "w") as fp:
            writer = csv.writer(fp)
            writer.writerows(data)

    yield Helper.new_school_year()
    rmtree(dir)


def test_write_cache(helper):
    helper.write_cache()
    cache = get_data_dir() / "cache"

    # some file matching this pattern is in the folder. Different platforms
    # will call it different things
    assert any("cache" in str(i) for i in get_data_dir().iterdir())

    # the slice is because we need to change `cache.db` to just `cache` at
    # the end of the path for shelve
    with shelve.open(str(cache), "r") as db:
        # `date` points to a datetime object
        assert isinstance(db["date"], datetime.datetime)
        date = cast(datetime.datetime, db["date"])

        # `date` is *almost* right now
        assert (datetime.datetime.now() - date).seconds < 1

        cached_helper = db["data"]
        assert isinstance(cached_helper, Helper)

        assert list(cached_helper.students.keys()) == list(helper.students.keys())
        assert list(cached_helper.homerooms.keys()) == list(helper.homerooms.keys())
        for key in helper.homerooms:
            a = helper.homerooms[key]
            b = cached_helper.homerooms[key]
            assert a.students == b.students
