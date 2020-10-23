import shelve
from pprint import pprint
import os
from pathlib import Path
from helper.ClassroomAutomator import FeedbackAutomator
from helper import Helper
from helper.zoom_attendance_report import MeetingSet, ExcelWriter


def main():
    report = MeetingSet(
        Path('data', 'zoom_attendance_reports'),
        trust_topics=True
    )
    report.process()
    pprint(report.groups)
    breakpoint()
    import sys
    sys.exit()
    # with shelve.open('cached_meetingset', 'r') as shelf:
    #     report = shelf['data']
    writer = ExcelWriter(report)
    writer.generate_report(Path('.', 'output.xlsx'))


if __name__ == '__main__':
    main()
