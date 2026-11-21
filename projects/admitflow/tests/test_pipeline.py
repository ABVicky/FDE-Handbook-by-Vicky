"""Pipeline, admissions matching, reporting and migrations (Module 05)."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("sqlalchemy")

from admitflow.cli import main  # noqa: E402
from admitflow.db import ImportRun, RejectedRow, SqlRepository  # noqa: E402
from admitflow.pipeline import _sis_phone, conversion_by_channel, counts, ingest, match_admissions  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


@pytest.fixture
def repo(tmp_path):
    return SqlRepository(f"sqlite:///{tmp_path / 'pipeline.db'}", create_tables=True)


def load_all(repo):
    return [ingest(repo, DATA / f, fmt) for f, fmt in
            [("leads_sample.csv", "website"), ("ad_leads.csv", "ads"), ("walkins.csv", "walkins")]]


def test_ingest_reports_reconcile(repo):
    reports = load_all(repo)
    assert [(r.rows_read, r.rows_loaded, r.rows_merged) for r in reports] == [(120, 120, 0), (60, 50, 10), (25, 20, 5)]
    assert counts(repo)["leads"] == 190


def test_same_file_is_skipped_unless_forced(repo):
    load_all(repo)
    assert ingest(repo, DATA / "ad_leads.csv", "ads").status == "skipped"
    forced = ingest(repo, DATA / "ad_leads.csv", "ads", force=True)
    assert (forced.rows_loaded, forced.rows_merged) == (0, 60)
    assert counts(repo)["leads"] == 190


def test_rejected_rows_are_stored_with_reasons(repo, tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text(
        "enquiry_id,received_at,name,phone,email,course,source\n"
        "X-1,not-a-date,Grace Patel,,,Accounting,website\n"
        "X-2,2026-09-01 10:00,Omar Ali,,omar@example.com,Accounting,website\n",
        encoding="utf-8",
    )
    report = ingest(repo, bad, "website")
    assert (report.rows_read, report.rows_loaded, report.rows_rejected) == (2, 1, 1)
    with repo.session() as s:
        (rejected,) = s.query(RejectedRow).all()
        assert rejected.line_num == 2 and "ValueError" in rejected.reason
        assert s.query(ImportRun).one().status == "succeeded"


@pytest.mark.parametrize(
    "raw, expected", [("02025550123", "+12025550123"), ("202-555-0123", "+12025550123"), ("", None), ("12", None)]
)
def test_sis_phone(raw, expected):
    assert _sis_phone(raw) == expected


def test_match_admissions_and_conversion(repo):
    load_all(repo)
    report = match_admissions(repo, DATA / "admissions_export.csv")
    assert report.matched == 22
    assert sorted(s for s, _ in report.unmatched) == ["NB260901", "NB260902", "NB260903"]
    again = match_admissions(repo, DATA / "admissions_export.csv")
    assert (again.matched, again.already_matched) == (0, 22)

    by_channel = {row["channel"]: row for row in conversion_by_channel(repo)}
    assert sum(row["leads"] for row in by_channel.values()) == 203
    assert by_channel["phone"]["enrolled"] == 3 and by_channel["phone"]["conversion"] == 0.25
    assert repo.list_leads(status="enrolled")[1] == 22


def test_cli_pipeline_commands(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'cli.db'}")
    SqlRepository(os.environ["DATABASE_URL"], create_tables=True)
    assert main(["ingest", "--website", str(DATA / "leads_sample.csv"), "--ads", str(DATA / "ad_leads.csv")]) == 0
    assert main(["match-admissions", str(DATA / "admissions_export.csv")]) == 0
    assert main(["report"]) == 0
    out = capsys.readouterr().out
    assert "ad_leads.csv: read 60, new 50, merged 10" in out and "website" in out
    assert main(["ingest"]) == 2


def test_cli_requires_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(SystemExit):
        main(["report"])


@pytest.mark.skipif(shutil.which("alembic") is None and not Path(sys.executable).with_name("alembic").exists(),
                    reason="alembic not installed")
def test_migrations_create_the_same_schema(tmp_path):
    """`alembic upgrade head` must produce a database the models agree with (no drift)."""
    alembic = shutil.which("alembic") or str(Path(sys.executable).with_name("alembic"))
    env = {**os.environ, "DATABASE_URL": f"sqlite:///{tmp_path / 'migrated.db'}"}
    for command in (["upgrade", "head"], ["check"], ["downgrade", "base"], ["upgrade", "head"]):
        result = subprocess.run([alembic, *command], cwd=ROOT, env=env, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
    repo = SqlRepository(env["DATABASE_URL"])
    ingest(repo, DATA / "walkins.csv", "walkins")
    assert counts(repo)["leads"] == 25
