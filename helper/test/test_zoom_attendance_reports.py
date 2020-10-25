from pathlib import Path

from pytest import fixture

from ..zoom_attendance_report import MeetingSet


@fixture
def trusted_topics_groups():
    fixture_dir = Path(
        Path(__file__).parents[2],  # repository base directory
        'data',
        'test_fixtures',
        'zoom_attendance_reports',
        'trust_topics',
    )
    report = MeetingSet(
        fixture_dir,
        trust_topics=True
    )
    report.process()
    return report


@fixture
def untrusted_topics_groups():
    fixture_dir = Path(
        Path(__file__).parents[2],  # repository base directory
        'data',
        'test_fixtures',
        'zoom_attendance_reports',
        'untrust_topics',
    )
    report = MeetingSet(
        fixture_dir,
        trust_topics=True
    )
    report.process()
    return report


def test_untrusted_topics_grouping(untrusted_topics_groups):
    report = untrusted_topics_groups
    for group in report.groups:
        group_topic = group[0].topic
        for meeting in group:
            print(group_topic)
            print(meeting.topic)
            assert meeting.topic == group_topic


def test_trusted_topics_grouping(trusted_topics_groups):
    gr = trusted_topics_groups
