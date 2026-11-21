"""Exercise 02 — reference: a transparent ROI model for AdmitFlow.

Every number is either measured (from the data) or an explicit, labelled assumption.
The model answers: "If AdmitFlow moves more enquiries into the 'contacted within 24 hours' group,
how many extra enrolments, and how much revenue, might that mean, against what it costs?"

Run: python roi_model.py   (standard library only)
"""
import csv
from pathlib import Path

DATA = Path(__file__).resolve().parents[4] / "projects" / "admitflow" / "data" / "historical_leads.csv"

# ---- ASSUMPTIONS: agree each one with the client (finance) and write down who agreed ----------
ASSUMPTIONS = {
    "enquiries_per_year": 9000,          # ~750/month (Module 01 brief: 600–900)
    "share_within_24h_before": 0.45,     # Head of Admissions' estimate (Module 01); measure it in the pilot
    "share_within_24h_after": 0.85,      # pilot target was 90%; be slightly conservative
    "revenue_per_enrolment": 4350,       # ~1,450 per term × 3 terms (fee schedule median); finance to confirm
    "margin_share": 0.35,                # share of fee revenue that is contribution (teaching costs etc. removed)
    "extra_counsellor_cost": 18000,      # contacting 85% within a day needs ~1 more part-time counsellor
    "causal_share": (0.25, 0.5, 0.75),   # how much of the observed gap is caused by speed (low / mid / high)
    "annual_running_cost": 3600,         # hosting + database + messaging + LLM, from the Module 06 estimate
    "one_off_cost": 30000,               # build and rollout (FDE time), illustrative
    "staff_hours_saved_per_week": 15,    # less copying between spreadsheets (counsellor interviews)
    "staff_cost_per_hour": 12,
}


def measured_rates(path=DATA):
    """Enrolment rate for leads contacted within 24 hours vs later (from two past intakes)."""
    fast, slow = [0, 0], [0, 0]
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            bucket = fast if float(row["hours_to_first_contact"]) < 24 else slow
            bucket[0] += 1
            bucket[1] += int(row["enrolled"])
    return fast[1] / fast[0], slow[1] / slow[0], fast[0] + slow[0]


def model(a=ASSUMPTIONS):
    rate_fast, rate_slow, n = measured_rates()
    shift = a["share_within_24h_after"] - a["share_within_24h_before"]
    gap = rate_fast - rate_slow
    scenarios = {}
    for label, causal in zip(("conservative", "middle", "optimistic"), a["causal_share"]):
        extra_enrolments = a["enquiries_per_year"] * shift * gap * causal
        revenue = extra_enrolments * a["revenue_per_enrolment"]
        contribution = revenue * a["margin_share"]
        time_saved = a["staff_hours_saved_per_week"] * 46 * a["staff_cost_per_hour"]
        annual_benefit = contribution + time_saved
        annual_cost = a["annual_running_cost"] + a["extra_counsellor_cost"]
        net_first_year = annual_benefit - annual_cost - a["one_off_cost"]
        payback_months = 12 * a["one_off_cost"] / max(annual_benefit - annual_cost, 1)
        scenarios[label] = {
            "extra_enrolments": round(extra_enrolments, 1),
            "extra_revenue": round(revenue),
            "contribution": round(contribution),
            "time_saved_value": round(time_saved),
            "net_first_year": round(net_first_year),
            "payback_months": round(payback_months, 1),
        }
    baseline = a["enquiries_per_year"] * (a["share_within_24h_before"] * rate_fast
                                          + (1 - a["share_within_24h_before"]) * rate_slow)
    return {"measured": {"rate_within_24h": round(rate_fast, 3), "rate_after_24h": round(rate_slow, 3),
                         "history_leads": n, "baseline_enrolments": round(baseline)}, "scenarios": scenarios}


if __name__ == "__main__":
    result = model()
    m = result["measured"]
    print(f"Measured on {m['history_leads']} past leads: enrolment {m['rate_within_24h']:.1%} if contacted within 24h, "
          f"{m['rate_after_24h']:.1%} if later.")
    print(f"Assumed shift: {ASSUMPTIONS['share_within_24h_before']:.0%} → {ASSUMPTIONS['share_within_24h_after']:.0%} "
          f"of {ASSUMPTIONS['enquiries_per_year']:,} enquiries a year contacted within 24h.\n")
    print(f"Today's expected enrolments from these enquiries: about {m['baseline_enrolments']} a year.\n")
    print(f"{'scenario':<14}{'extra enrol.':>13}{'vs today':>10}{'revenue':>11}{'contribution':>14}{'net year 1':>12}{'payback':>10}")
    for name, s in result["scenarios"].items():
        uplift = s["extra_enrolments"] / m["baseline_enrolments"]
        print(f"{name:<14}{s['extra_enrolments']:>13}{uplift:>10.0%}{s['extra_revenue']:>11,}{s['contribution']:>14,}"
              f"{s['net_first_year']:>12,}{s['payback_months']:>8} mo")
    print("\nSanity check: if even the conservative case pays back within months, ask what's missing (capacity,")
    print("seasonality, competitors, data quality) before presenting it.")
    print("Caveat: the history shows correlation. 'causal_share' is our honest uncertainty about how much of")
    print("the gap speed itself causes. The pilot (Module 01 metrics) is how we find out.")
    mid = result["scenarios"]["middle"]
    assert result["scenarios"]["conservative"]["extra_enrolments"] < mid["extra_enrolments"]
    assert mid["payback_months"] > 0
