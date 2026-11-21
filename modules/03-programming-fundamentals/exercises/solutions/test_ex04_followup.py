from datetime import datetime, timedelta

import pytest

from ex04_followup import FollowUp, overdue, per_counsellor

NOW = datetime(2026, 9, 15, 12, 0)


def fu(lead_id, hours_from_now, counsellor="Priya", done=False):
    return FollowUp(lead_id, NOW + timedelta(hours=hours_from_now), counsellor, done)


@pytest.mark.parametrize(
    "hours, done, expected",
    [
        (-1, False, True),    # an hour ago, not done
        (0, False, False),    # exactly now: not overdue yet
        (1, False, False),    # in the future
        (-48, True, False),   # done follow-ups are never overdue
    ],
)
def test_is_overdue(hours, done, expected):
    assert fu("ENQ-1", hours, done=done).is_overdue(NOW) is expected


def test_complete_marks_done_and_records_note():
    item = fu("ENQ-1", -1)
    item.complete("called, booked a visit")
    assert item.done
    assert item.notes == ["called, booked a visit"]


def test_complete_twice_raises():
    item = fu("ENQ-1", -1)
    item.complete("called")
    with pytest.raises(ValueError, match="already done"):
        item.complete("called again")


def test_notes_are_not_shared_between_instances():
    a, b = fu("A", 1), fu("B", 1)
    a.notes.append("only for A")
    assert b.notes == []


def test_overdue_sorted_oldest_first():
    items = [fu("new", -1), fu("old", -30), fu("future", 5), fu("mid", -10)]
    assert [f.lead_id for f in overdue(items, NOW)] == ["old", "mid", "new"]


def test_per_counsellor():
    items = [fu("1", -1, "Priya"), fu("2", -2, "Priya"), fu("3", -3, "Omar"), fu("4", 3, "Omar")]
    assert per_counsellor(items, NOW) == {"Priya": 2, "Omar": 1}
