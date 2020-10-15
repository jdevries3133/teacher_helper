"""
Parses a directory full of zoom attendance reports and creates a
longitudinal master report, which shows which students attend over time
in a recurring meeitng.
"""
from pathlib import Path

from helper import ZoomAttendanceReport


def zoom_attendance():
    reporter = ZoomAttendanceReport(Path('data', 'zoom_attendance_reports'))
    reporter.rename_csv_files()
    reporter.generate_report(Path('.'))


def all_():
    """
    Update all reports
    """
    zoom_attendance()


if __name__ == '__main__':
    all_()
