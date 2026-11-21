"""Exercise set 01 — reference solutions. Run: python3 ex01_basics.py"""
from datetime import datetime

FMT = "%Y-%m-%d %H:%M"


def priority(hours_waiting):
    if hours_waiting < 0:
        raise ValueError("hours_waiting cannot be negative")
    if hours_waiting > 48:
        return "urgent"
    if hours_waiting > 24:
        return "high"
    return "normal"


def hours_between(start, end):
    delta = datetime.strptime(end, FMT) - datetime.strptime(start, FMT)
    return delta.total_seconds() / 3600


def followup_schedule(days):
    printed = []
    for day in range(1, days + 1):
        if day == 25:
            break
        value = "follow up" if day % 7 == 0 else day
        print(value)
        printed.append(value)
    return printed


def late_count(waits, limit=24):
    count = 0
    for hours in waits:
        if hours > limit:
            count += 1
    return count


def format_rate(admissions, enquiries):
    if enquiries == 0:
        return "n/a"
    return f"{admissions / enquiries:.1%}"


# 6. bool("False") -> True  (any non-empty string is truthy)
#    "5" * 3       -> "555" (repeating a string)
#    7 // 2        -> 3     (floor division)
#    0.1 + 0.2 == 0.3 -> False (floats are binary approximations)


if __name__ == "__main__":
    assert priority(30) == "high" and priority(49) == "urgent" and priority(24) == "normal"
    try:
        priority(-1)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    assert hours_between("2026-09-01 10:00", "2026-09-02 16:30") == 30.5
    out = followup_schedule(30)
    assert len(out) == 24 and out[6] == "follow up" and out[-1] == 24
    assert late_count([2, 30, 5, 49, 26, 1]) == 3
    assert format_rate(11, 120) == "9.2%" and format_rate(0, 0) == "n/a"
    assert bool("False") is True and "5" * 3 == "555" and 7 // 2 == 3 and 0.1 + 0.2 != 0.3
    print("all checks passed")
