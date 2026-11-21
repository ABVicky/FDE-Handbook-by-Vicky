# Lesson 05 — Monitoring and alerting

**Time:** ~5 hours · **Core**

## The three signals

| Signal | Answers | AdmitFlow |
| --- | --- | --- |
| **Logs** | What happened in this request? | Structured request logs with `request_id`, redacted |
| **Metrics** | How is the system behaving overall, over time? | `/metrics`: request counts, latency histogram, outbox, assistant, logins |
| **Traces** | Where did the time go across components? | *Stretch:* OpenTelemetry spans for API → retrieval → LLM → database |

Logs are for **investigating**; metrics are for **detecting** and **alerting**. The Module 10 incident had 1,125 warnings in a log and no alert.

## Metrics in AdmitFlow

[`observability.py`](../../../projects/admitflow/admitflow/observability.py) is a small registry rendering the Prometheus text format:

```
admitflow_http_requests_total{method="GET",route="/leads",status="200"} 412
admitflow_http_request_seconds_bucket{route="/leads",le="0.05"} 398
admitflow_outbox_oldest_approved_minutes 0
admitflow_assistant_questions_total{answered="True",engine="offline"} 87
```

Design points:
- Label by **route template** (`/leads/{lead_id}`), never the raw URL. Raw URLs create a new time series per lead ("cardinality explosion").
- Never put personal data or unbounded values in labels.
- `/metrics` requires a bearer token, because even metrics can leak information.

In larger systems, use `prometheus_client` or **OpenTelemetry** (vendor-neutral instrumentation that exports metrics, traces and logs to Grafana, Datadog, cloud monitoring and others). The concepts transfer directly.

## SLIs, SLOs and error budgets

- **SLI** (indicator): a measurement of user experience, e.g. the share of requests that don't fail.
- **SLO** (objective): the target, e.g. 99.5% per month.
- **Error budget:** what the SLO allows to fail (0.5% ≈ 3.6 hours a month). While budget remains, ship features; when it's spent, focus on reliability.

AdmitFlow's SLOs are in the [runbook](../../../projects/admitflow/docs/runbook.md#service-level-objectives-slos): availability 99.5%, GET /leads p95 < 500 ms, 99% of approved messages sent within 15 minutes, 100% of fee answers correct before each release.

Choose SLOs **with the client**, from what users need ("counsellors work 9am–7pm"), not 99.999% because it sounds good. Every extra nine costs real money.

## Alerts that people trust

[`deploy/monitoring/alerts.yml`](../../../projects/admitflow/deploy/monitoring/alerts.yml) defines seven alerts. Rules for good alerts:
- **Alert on symptoms users feel** (errors, latency, messages not sent), not on every cause (CPU at 80%).
- Every alert has a **runbook link** and a clear first action.
- **Page** only for things needing action now; open a **ticket** for the rest. Too many pages and people stop responding.
- Use `for:` durations to avoid alerts on brief blips.
- Test alerts: the break & fix simulation shows `AdmitFlowOutboxStuck` would have fired one hour after the token expired.

## Dashboards

One page that answers "is AdmitFlow OK?": request rate, error rate, p95 latency, outbox backlog, assistant answered/declined, failed logins, and the SLO budget remaining. Show the business metric too (leads contacted within 24 hours), because that's what Ms. Rao cares about.

## Synthetic checks

An external probe that calls `/health` (and ideally logs in with a test account) every minute catches "the whole site is down" even when your own monitoring is down with it. Most clouds and monitoring tools offer one.

## Check yourself

Run Prometheus locally (Docker) scraping AdmitFlow's `/metrics` with the token, load `alerts.yml`, and make `AdmitFlowOutboxStuck` fire by approving a draft with no sender configured. Then write the dashboard panel list for Mr. Okafor.

Next: [Lesson 06 — Reliability patterns](06-reliability-patterns.md)
