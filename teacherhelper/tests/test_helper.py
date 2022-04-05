"""This tests that the deprecated `helper` interface still works."""

import csv
import random
from typing import cast
from shutil import rmtree
import shelve
import datetime
from tempfile import mkdtemp
from pathlib import Path
from unittest.mock import patch
from webbrowser import get

import pytest

from .._data_dir import get_data_dir
from ..sis.tests.fixtures import students_csv, parents_csv
from ..helper import Helper, get_helper


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


@pytest.fixture(params=(list(range(5))))
def random_student(request, helper):
    """10 random helper students"""
    random.seed(request.param)
    return random.choice(list(helper.students.values()))


@pytest.fixture(params=list(range(5)))
def random_parent(request, helper):
    random.seed(request.param)
    all_guardians = set(i for g in helper.students.values() for i in g.guardians)
    return random.choice(list(all_guardians))


def check_helper_equality(a: Helper, b: Helper) -> bool:
    """Rough __eq__ check for helper objects"""
    try:
        assert isinstance(a, Helper)
        assert isinstance(b, Helper)

        assert list(a.students.keys()) == list(b.students.keys())
        assert list(a.homerooms.keys()) == list(b.homerooms.keys())
        for key in a.homerooms:
            x = a.homerooms[key]
            y = b.homerooms[key]
            assert x.students == y.students

        return True
    except AssertionError:
        return False


def test_get_helper(helper):
    """Smoke test for the entrypoint function"""
    # get_helper will read from a cached helper
    helper.write_cache()
    helper_ret = get_helper()
    check_helper_equality(helper, helper_ret)


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

        cached_helper = cast(Helper, db["data"])
        check_helper_equality(cached_helper, helper)


def test_read_cache(helper):
    helper.write_cache()
    cached_helper = Helper.read_cache()
    check_helper_equality(helper, cached_helper)


def test_find_nearest_match(helper, random_student):
    name = random_student.name
    changed = list(name)
    changed[3] = "b"
    changed = "".join(changed)

    with patch("teacherhelper.sis._sis.process.extractOne") as p:

        # 89 is below the default threshold of 90
        p.return_value = name, 89
        result = helper.find_nearest_match(changed)
        assert p.mock_calls[-1].args[0] == changed
        assert result is None

        # if we lower the threshold, we get a result
        p.return_value = name, 89
        result = helper.find_nearest_match(changed, threshold=88)
        assert p.mock_calls[-1].args[0] == changed
        assert result is random_student

        # if we raise the confidence of the search result, we get a result
        p.return_value = name, 95
        result = helper.find_nearest_match(changed)
        assert p.mock_calls[-1].args[0] == changed
        assert result is random_student

        for call in p.mock_calls:
            assert call.args[1] == helper.students.keys()


def test_find_parent(helper, random_parent):
    name = random_parent.name
    result = helper.find_parent(name)
    assert result
    assert random_parent in result.guardians

    # fuzzy matches work too
    chars = list(name)
    chars[1] = "c"
    chars[4] = "e"
    name = "".join(chars)
    result = helper.find_parent(name)
    assert result
    assert random_parent in result.guardians


def test_deprecation_warning_raised(helper):
    """get_helper and Helper.__init__ should cause a deprecation warnings"""
    with pytest.deprecated_call():
        Helper({}, {}, {})

    # below does not work if cache does not exist. This will write into temp
    # dir because of helper fixture
    helper.write_cache()
    with pytest.deprecated_call():
        get_helper()
