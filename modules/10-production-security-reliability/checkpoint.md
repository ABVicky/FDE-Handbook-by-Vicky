# Module 10 — Checkpoint

Pass mark: **10 / 12**, plus the [build](build.md) and [break & fix](break-and-fix/README.md).

---

**1.** Name the six STRIDE categories, with one AdmitFlow example each.

**2.** Why rate-limit login by username *and* by IP? What's the catch with an in-memory limiter behind a load balancer?

**3.** What does `Cache-Control: no-store` protect against on an API that returns student records?

**4.** Give two reasons not to log phone numbers, and one way the redaction filter could go wrong.

**5.** What's the difference between an SLI, an SLO and an error budget? Give AdmitFlow examples.

**6.** Why label metrics by route template (`/leads/{lead_id}`) rather than the actual path?

**7.** "Alert on symptoms, not causes." What does that mean? Give one good and one bad alert.

**8.** A dependency returns 401. Should the outbox keep retrying every hour? What should happen instead?

**9.** What is graceful degradation? What does AdmitFlow do when the LLM provider is down?

**10.** During an incident, what do you do first: find the root cause, or restore service? Why?

**11.** What makes an incident review "blameless", and why does it matter?

**12.** Define RPO and RTO. What does "a backup you haven't restored is a hope" mean in practice?

---

<details>
<summary><strong>Answers</strong></summary>

1. Spoofing (forged webhook), Tampering (edited form body), Repudiation ("I didn't approve that"), Information disclosure (another counsellor's leads, logs), Denial of service (flooding the assistant), Elevation of privilege (counsellor assigning leads, agent sending messages).
2. Username limits stop many-IP attacks on one account; IP limits stop one source trying many accounts. In-memory limits are per instance (N instances = N× the limit), and behind a proxy all clients may appear as one IP unless forwarded headers are configured correctly.
3. Browsers, proxies and CDNs storing personal data, so it can't be read later from a shared computer or cache.
4. Logs are copied widely and kept long; they're read by people without access to the data. Redaction can over-match (masking timestamps, making logs useless) or under-match (missing unusual formats). Test it on realistic lines.
5. SLI: a measurement (share of non-5xx requests). SLO: a target for it (99.5%/month). Error budget: the allowed failure (0.5% ≈ 3.6 h/month). Also: 99% of approved messages sent within 15 minutes.
6. Each distinct label value creates a time series; raw paths create one per lead (unbounded cardinality), which breaks monitoring systems and may leak IDs.
7. Alert on what users experience. Good: approved messages waiting > 30 min; 5xx rate > 2%. Bad: CPU > 80% (may be fine), any single warning log line.
8. No. A 401 won't fix itself. Stop retrying that channel, alert immediately, and keep the drafts queued until the credential is fixed.
9. Keeping the core working when a part fails. AdmitFlow falls back to the offline assistant and the template drafter.
10. Restore service first (rollback, fallback, restart); then diagnose. Users care about service; the evidence can usually be kept (logs, metrics) while you mitigate.
11. It focuses on how the system allowed the mistake, not on who made it. People then report problems honestly, and fixes target the system so it can't recur.
12. RPO: maximum acceptable data loss (time). RTO: maximum acceptable downtime. Untested backups often fail (corrupt, incomplete, missing permissions, unknown procedure), so you schedule restore drills and record them.

</details>
