"""End-to-end tests: run the CLI exactly as a counsellor would."""
import csv
import json
from pathlib import Path

import pytest

from admitflow.cli import main

DATA = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture
def store(tmp_path, monkeypatch):
    path = tmp_path / "leads.json"
    monkeypatch.setenv("ADMITFLOW_STORE", str(path))
    return path


def import_all():
    return main(
        [
            "import",
            "--website", str(DATA / "leads_sample.csv"),
            "--ads", str(DATA / "ad_leads.csv"),
            "--walkins", str(DATA / "walkins.csv"),
        ]
    )


def test_import_dedupes_sample_data(store, capsys):
    assert import_all() == 0
    out = capsys.readouterr().out
    assert "15 duplicate(s) merged; 190 new; 190 unique lead(s)" in out
    assert len(json.loads(store.read_text(encoding="utf-8"))["leads"]) == 190


def test_importing_twice_creates_no_new_leads(store, capsys):
    import_all()
    import_all()
    assert len(json.loads(store.read_text(encoding="utf-8"))["leads"]) == 190


def test_stats(store, capsys):
    import_all()
    capsys.readouterr()
    assert main(["stats"]) == 0
    out = capsys.readouterr().out
    assert "Unique leads: 190" in out
    assert "Enquired through more than one channel: 11" in out


def test_search_finds_non_english_names(store, capsys):
    import_all()
    capsys.readouterr()
    main(["search", "nguyễn"])
    out = capsys.readouterr().out
    assert "Nguyễn" in out
    assert "lead(s)" in out


def test_list_filters(store, capsys):
    import_all()
    capsys.readouterr()
    main(["list", "--source", "whatsapp", "--course", "nursing"])
    out = capsys.readouterr().out
    assert "4 lead(s)" in out


def test_export_csv(store, tmp_path, capsys):
    import_all()
    out_file = tmp_path / "out.csv"
    assert main(["export", str(out_file), "--source", "walk-in"]) == 0
    with open(out_file, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert rows and all("walk-in" in row["sources"] for row in rows)


def test_import_without_files_fails(store, capsys):
    assert main(["import"]) == 2
    assert "nothing to import" in capsys.readouterr().err


def test_missing_file_gives_clear_error(store, capsys):
    assert main(["import", "--website", "nope.csv"]) == 1
    assert "file not found: nope.csv" in capsys.readouterr().err


def test_rejected_rows_are_shown(store, tmp_path, capsys):
    bad = tmp_path / "bad.csv"
    bad.write_text(
        "enquiry_id,received_at,name,phone,email,course,source\n"
        "ENQ-1,not a date,Grace Patel,,,Accounting,website\n"
        "ENQ-2,2026-09-02 11:00,Omar Ali,,o@example.com,Accounting,website\n",
        encoding="utf-8",
    )
    assert main(["-v", "import", "--website", str(bad)]) == 0
    captured = capsys.readouterr()
    assert "1 imported, 1 rejected" in captured.out
    assert "line 2" in captured.err


def test_cli_and_api_share_one_store(store, capsys, monkeypatch):
    """Users created for the API must survive a later CLI import, and vice versa."""
    pytest.importorskip("jwt")
    import_all()
    assert main(["create-user", "priya", "--full-name", "Priya Nair", "--password", "a-long-test-password"]) == 0
    import_all()
    data = json.loads(store.read_text(encoding="utf-8"))
    assert [u["username"] for u in data["users"]] == ["priya"]
    assert len(data["leads"]) == 190
    assert main(["create-user", "omar", "--full-name", "Omar", "--password", "short"]) == 2
