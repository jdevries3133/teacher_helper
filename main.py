import os
from pathlib import Path
from pprint import pprint
from helper.ClassroomAutomator import FeedbackAutomator
from helper import Helper
from helper.zoom_attendance_report import MeetingSet

if __name__ == '__main__':
    report = MeetingSet(
        Path('data', 'zoom_attendance_reports'),
        trust_topics=True
    )
    report.process()
    breakpoint()
