from datetime import datetime
from pathlib import Path

import pytest

from admitflow.importers import import_file

DATA = Path(__file__).resolve().parent.parent / "data"


def write(tmp_path, name, text, encoding="utf-8"):
    path = tmp_path / name
    path.write_text(text, encoding=encoding)
    return path


def test_sample_files_import_completely():
    assert len(import_file(DATA / "leads_sample.csv", "website").leads) == 120
    assert len(import_file(DATA / "ad_leads.csv", "ads").leads) == 60
    assert len(import_file(DATA / "walkins.csv", "walkins").leads) == 25


def test_website_handles_quoted_comma_and_blank_lines(tmp_path):
    path = write(
        tmp_path,
        "w.csv",
        "enquiry_id,received_at,name,phone,email,course,source\n"
        'ENQ-1,2026-09-01 10:00,"Lee, Chloe",+1 202-555-0101,C@Example.com,Accounting,Website \n'
        "\n"
        "ENQ-2,2026-09-02 11:00,Zoë Müller,,,DA,whatsapp\n",
    )
    result = import_file(path, "website")
    assert [lead.name for lead in result.leads] == ["Chloe Lee", "Zoë Müller"]
    first = result.leads[0]
    assert first.email == "c@example.com"
    assert first.phone == "+12025550101"
    assert first.sources == ["website"]
    assert result.leads[1].course == "Data Analytics"


def test_bad_rows_are_reported_not_dropped(tmp_path):
    path = write(
        tmp_path,
        "w.csv",
        "enquiry_id,received_at,name,phone,email,course,source\n"
        "ENQ-1,yesterday,Grace Patel,,,Accounting,website\n"
        "ENQ-2,2026-09-02 11:00,Omar Ali,,,Accounting,fax\n"
        "ENQ-3,2026-09-02 11:00,,,,Accounting,website\n",
    )
    result = import_file(path, "website")
    assert result.leads == []
    assert [line for line, _ in result.rejected] == [2, 3, 4]
    assert "missing name" in result.rejected[2][1]


def test_walkins_with_excel_bom_and_day_first_dates(tmp_path):
    path = write(
        tmp_path,
        "walk.csv",
        "Date,Name,Contact,Course,Notes\n"
        "04/09/2026,  LUCÍA  FERNÁNDEZ ,lucia@example.net,Business Admin,asked about fees\n"
        "05/09/2026,Kai Tanaka,202 555 0154,Digital Mktg,\n",
        encoding="utf-8-sig",
    )
    result = import_file(path, "walkins")
    lucia, kai = result.leads
    assert lucia.received_at == datetime(2026, 9, 4)  # 4 September, not 9 April
    assert lucia.name == "Lucía Fernández"
    assert lucia.email == "lucia@example.net" and lucia.phone is None
    assert kai.phone == "+12025550154" and kai.email is None
    assert lucia.lead_id.startswith("WALKIN-")


def test_ads_format(tmp_path):
    path = write(
        tmp_path,
        "ads.csv",
        "lead_id,created_time,full_name,phone_number,email,program_interest,campaign_name\n"
        "ad_1,2026-09-01T12:26:00Z,nguyễn thu,(202) 555-0112,t@example.org,web_dev,sept_intake_search\n",
    )
    (lead,) = import_file(path, "ads").leads
    assert lead.name == "Nguyễn Thu"
    assert lead.course == "Web Development"
    assert lead.notes == "campaign: sept_intake_search"


def test_unknown_format_raises():
    with pytest.raises(ValueError):
        import_file(DATA / "ad_leads.csv", "fax")
