import json
from pathlib import Path
import unittest

from pytest import fixture

from ..zoom_attendance_report import MeetingSet, ExcelWriter
from ..helper import Helper


class TestMeetingSet(unittest.TestCase):
    """
    This is ultimately more of a regression test because it uses real data 
    """
    def setUp(self):
        self.helper = Helper.read_cache()   # poor test independence;
                                            # also requires testing w/ real
                                            # data
        with open('sample_data_secret.json', 'r') as jsn:
            self.data = json.load(jsn)

    def test_meeting_(self):


