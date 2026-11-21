"""The same three days, with the AdmitFlowOutboxStuck alert from deploy/monitoring/alerts.yml:
fire when the oldest approved draft has waited more than 30 minutes, for 5 minutes (here: one hourly check)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent), str(HERE.parents[3] / "projects" / "admitflow")]
from simulate_incident import TOKEN_EXPIRES, run  # noqa: E402

from admitflow.observability import metrics  # noqa: E402

fired = []


def outbox_stuck(now):
    firing = metrics.value("admitflow_outbox_oldest_approved_minutes") > 30
    if firing and not fired:
        fired.append(now)
    return firing


result = run(alert_check=outbox_stuck)
first = fired[0]
print(f"token expired:      {TOKEN_EXPIRES:%a %H:%M}")
print(f"alert first fired:  {first:%a %H:%M}  ({(first - TOKEN_EXPIRES).total_seconds() / 3600:.0f} h later)")
print(f"follow-ups waiting when the alert fired: a handful, instead of {result['stuck']} by the time a parent called")
assert (first - TOKEN_EXPIRES).total_seconds() <= 2 * 3600
