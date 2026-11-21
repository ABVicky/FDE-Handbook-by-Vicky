"""Regression tests: these would have caught the original bug."""
import pytest

from clean_ad_leads import clean_name, main


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("José García", "José García"),
        ("Nguyễn Thu", "Nguyễn Thu"),
        ("Ølaf Berg", "Ølaf Berg"),
        ("प्रिया शर्मा", "प्रिया शर्मा"),
        ("seán o'brien", "Seán O'Brien"),
        ("  Ana-María   López ", "Ana-María López"),
    ],
)
def test_international_names_are_kept(raw, expected):
    assert clean_name(raw) == expected


@pytest.mark.parametrize("raw", ["", "   ", "1234", "---"])
def test_names_without_letters_are_rejected(raw):
    with pytest.raises(ValueError):
        clean_name(raw)


def test_no_rows_disappear(tmp_path):
    src = tmp_path / "in.csv"
    src.write_text(
        "lead_id,created_time,full_name,phone_number,email,program_interest,campaign_name\n"
        "a,t,Zoë Müller,(202) 555-0101,Z@x.org,web_dev,c\n"
        "b,t,1234,,b@x.org,web_dev,c\n",
        encoding="utf-8",
    )
    dst = tmp_path / "out.csv"
    assert main(src, dst) == 1  # non-zero: something was rejected and needs a human look
    lines = dst.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2 and "Zoë Müller" in lines[1]
