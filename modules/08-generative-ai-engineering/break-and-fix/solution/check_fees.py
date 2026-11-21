"""Regression check: the assistant must quote current fees and never superseded ones.

Run from this folder with the admitflow package installed: python check_fees.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4] / "projects" / "admitflow"
sys.path.insert(0, str(ROOT))
from admitflow.assistant import build_assistant  # noqa: E402

CURRENT = {"Data Analytics": "1,800", "Web Development": "1,650", "Digital Marketing": "1,400",
           "Accounting": "1,250", "Business Administration": "1,500", "Nursing Assistance": "1,350"}
OUTDATED = {"Data Analytics": "1,650", "Digital Marketing": "1,300", "Accounting": "1,150",
            "Business Administration": "1,400", "Nursing Assistance": "1,250"}   # Web Development's 2025 fee was 1,550

assistant = build_assistant(str(ROOT / "data" / "course_docs"), "offline")
failures = 0
for course, fee in CURRENT.items():
    for question in (f"How much is {course}?", f"What are the fees for {course}?", f"{course} fee per term"):
        answer, hits = assistant.ask(question)
        wrong = OUTDATED.get(course)
        ok = fee in answer.text and (wrong is None or wrong not in answer.text) and all(not h.chunk.superseded for h in hits)
        failures += not ok
        print(f"[{'ok ' if ok else 'FAIL'}] {question!r} → {answer.text[:70]}")
print(f"\n{18 - failures}/18 fee answers correct")
sys.exit(1 if failures else 0)
