import shelve
from pprint import pprint
import os
from pathlib import Path
from pyautogc import FeedbackAutomator
from teacherHelper import Helper
from teacherHelper.zoom_attendance_report import MeetingSet, ExcelWriter


def main():
    report = MeetingSet(
        Path('data', 'test_fixtures', 'zoom_attendance_reports', 'untrust_topics'),
        trust_topics=False
    )
    report.process()
    pprint(report.groups)
    # breakpoint()
    # import sys
    # sys.exit()
    # with shelve.open('cached_meetingset', 'r') as shelf:
    #     report = shelf['data']
    # writer = ExcelWriter(report)
    # writer.generate_report(Path('.', 'output.xlsx'))


if __name__ == '__main__':
    main()
