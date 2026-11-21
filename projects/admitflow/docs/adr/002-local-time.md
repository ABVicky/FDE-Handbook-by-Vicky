# ADR-002: Store times as institute local time

**Status:** Accepted · **Date:** Module 04

## Context
Source exports contain local times without a time zone (`2026-09-01 10:55`, `04/09/2026`). Counsellors think in local time ("call back at 4pm"). The institute operates in one time zone.

## Decision
AdmitFlow stores **naive datetimes in the institute's local time zone**. The server runs with `TZ` set to the institute's zone (e.g. `TZ=Asia/Kolkata`). Any time received *with* an offset (`…Z`, `+05:30`) is **converted** to local time on input, never just stripped.

## Consequences
- ✅ Matches the source data and how users think.
- ⚠️ If the institute opens a campus in another time zone, migrate to timezone-aware UTC storage. Record that as a new ADR.
- ⚠️ Servers and CI must set `TZ` explicitly; tests cover both local and UTC.

## Alternatives considered
- **Aware UTC everywhere** (the usual best practice for multi-region systems): more correct in general, but every imported value would need an assumed zone anyway, and the display layer would need converting everywhere. Revisit if the context changes.
