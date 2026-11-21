"""Lead scoring (Module 07). Skipped if the `ml` extra isn't installed."""
import json
import warnings
from datetime import datetime
from pathlib import Path

import pytest

pytest.importorskip("sklearn")
warnings.filterwarnings("ignore", category=RuntimeWarning)  # spurious BLAS warnings on some macOS builds

from admitflow.cli import main  # noqa: E402
from admitflow.models import Lead  # noqa: E402
from admitflow.scoring import (  # noqa: E402
    FEATURES,
    LeadScorer,
    conversion_by_response_time,
    features_from_lead,
    precision_at_k,
    save,
    train,
)

DATA = Path(__file__).resolve().parent.parent / "data"
HISTORY = DATA / "historical_leads.csv"


@pytest.fixture(scope="module")
def trained(tmp_path_factory):
    result = train(HISTORY)
    path = tmp_path_factory.mktemp("model") / "lead_score.joblib"
    save(result, path)
    return result, path


def lead(**overrides):
    base = dict(lead_id="T-1", received_at=datetime(2026, 9, 15, 11, 0), name="Test Lead", phone="+12025550100",
                email="t@example.org", course="Accounting", sources=["website"])
    base.update(overrides)
    return Lead(**base)


def test_no_leakage_features():
    """Only information available at enquiry time may be used."""
    forbidden = {"hours_to_first_contact", "contacts_first_week", "fee_paid", "days_to_final_status", "enrolled"}
    assert not forbidden & set(FEATURES)


def test_temporal_split_and_metrics(trained):
    result, _ = trained
    assert (result.train_rows, result.test_rows) == (1500, 1500)
    for name in ("baseline", "model"):
        m = result.metrics[name]
        assert 0.5 < m["roc_auc"] < 0.8          # better than chance, and no suspicious "perfect" score
        assert m["precision_at_20pct"] > m["base_rate"]


def test_model_is_only_marginally_better_than_the_baseline(trained):
    """The honest finding this module teaches: enquiry-time data carries little extra signal."""
    m, b = trained[0].metrics["model"], trained[0].metrics["baseline"]
    assert abs(m["roc_auc"] - b["roc_auc"]) < 0.05


def test_precision_at_k():
    assert precision_at_k([1, 0, 1, 0], [0.9, 0.8, 0.1, 0.2], 0.5) == 0.5
    assert precision_at_k([1, 0], [0.9, 0.1], 0.01) == 1.0   # at least one lead


def test_walk_in_date_only_is_not_out_of_hours():
    walk_in = lead(sources=["walk-in"], received_at=datetime(2026, 9, 4))
    late_web = lead(received_at=datetime(2026, 9, 4, 23, 30))
    assert features_from_lead(walk_in)["out_of_hours"] == 0
    assert features_from_lead(late_web)["out_of_hours"] == 1
    assert features_from_lead(lead(sources=["ad", "walk-in"]))["extra_channels"] == 1


def test_scores_and_explanations(trained):
    scorer = LeadScorer(trained[1])
    walk_in = scorer.score(lead(sources=["walk-in"]))
    ad = scorer.score(lead(sources=["ad"]))
    assert walk_in.probability > ad.probability
    assert walk_in.factors[0] == "+ came via walk-in" and ad.factors[0] == "− came via ad"
    assert walk_in.model_version == "lead-score-1"
    assert json.loads(trained[1].with_suffix(".json").read_text())["features"] == FEATURES


def test_unknown_course_does_not_crash(trained):
    assert 0 < LeadScorer(trained[1]).score(lead(course="Robotics")).probability < 1


def test_response_time_analysis():
    rows = {r["bucket"]: r for r in conversion_by_response_time(HISTORY)}
    assert sum(r["leads"] for r in rows.values()) == 3000
    assert rows["1–24 hours"]["rate"] > 5 * rows["over 72 hours"]["rate"]


def test_cli_train_model(tmp_path, capsys):
    out = tmp_path / "m.joblib"
    assert main(["train-model", str(HISTORY), "--out", str(out)]) == 0
    printed = capsys.readouterr().out
    assert "baseline" in printed and "over 72 hours" in printed and out.exists()


# -- API ------------------------------------------------------------------------------

def test_score_and_priority_endpoints(trained, tmp_path, monkeypatch):
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from admitflow.api import create_app
    from admitflow.auth import create_token
    from admitflow.importers import import_file
    from admitflow.models import User
    from admitflow.repository import JsonRepository

    monkeypatch.setenv("ADMITFLOW_SECRET_KEY", "test-secret-key-that-is-long-enough-1234567890")
    repo = JsonRepository(tmp_path / "s.json")
    repo.add_leads(import_file(DATA / "walkins.csv", "walkins").leads)
    repo.save_user(User("priya", "Priya", "counsellor", "x"))
    headers = {"Authorization": f"Bearer {create_token('priya', 'counsellor')}"}

    client = TestClient(create_app(repo, scorer=LeadScorer(trained[1])))
    body = client.get("/leads/WALKIN-0002/score", headers=headers).json()
    assert body["band"] in ("high", "medium", "low") and body["factors"]
    queue = client.get("/leads/priority", params={"limit": 5}, headers=headers).json()
    assert len(queue) == 5 and queue[0]["score"] >= queue[-1]["score"]
    assert client.get("/leads/NOPE/score", headers=headers).status_code == 404

    no_model = TestClient(create_app(repo, scorer=None))
    monkeypatch.setenv("ADMITFLOW_MODEL", str(tmp_path / "missing.joblib"))
    no_model.app.state.scorer = None
    assert no_model.get("/leads/WALKIN-0002/score", headers=headers).status_code == 503
