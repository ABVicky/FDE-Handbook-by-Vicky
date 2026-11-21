# Lesson 02 — Integration patterns

**Time:** ~3 hours · **Core**

## The main patterns

| Pattern | How | Latency | Good for | Watch out for |
| --- | --- | --- | --- | --- |
| **Request/response API** | You call their REST/GraphQL API | Immediate | Look-ups, writes | Rate limits, their downtime |
| **Webhooks (push)** | They call *your* endpoint when something happens | Seconds | New form submissions, payment events | Security, duplicates, missed events |
| **Polling** | You ask "anything new since X?" on a schedule | Minutes | Systems without webhooks | Load, cursors, gaps |
| **File transfer** | CSV/JSON/Parquet dropped in a folder or bucket | Hours/days | Legacy systems, bulk data | Formats, partial files, schedules |
| **Message queue / event stream** | Producers publish events; consumers subscribe | Seconds | Decoupled, high-volume systems | Ordering, replays, operational complexity |
| **Change data capture (CDC)** | Stream every database change (Debezium, cloud CDC) | Seconds | Replicating databases | Needs DB access; schema changes |
| **Direct database read** | Query their database or a replica | Immediate | When nothing else exists | Coupling to internals; permissions |

AdmitFlow uses four: **webhooks** (website form), **files** (ad export, SIS export), **API calls** (CRM, messaging) and an **MCP server** (AI tools).

## Choosing

Ask:
1. **How fresh must it be?** A weekly enrolment report doesn't need streaming.
2. **What does the other side support?** Often this decides it.
3. **Who operates it?** A queue cluster is one more thing the client must run.
4. **What happens when it fails?** Can you detect gaps and replay?

The simplest pattern that meets the freshness need usually wins.

## Push vs. pull, and combining them

Webhooks are fast but can be missed (your API was down; their retries gave up). A robust design often **combines** them: webhooks for speed, plus a periodic **reconciliation** poll or export that catches anything missed. AdmitFlow could re-import the website's daily export and rely on dedupe to ignore what webhooks already delivered.

## The outbox pattern

When a database change must trigger a message to another system (send an email, sync a CRM), don't do both inside one request and hope neither fails. Instead:

1. In your transaction, write the change **and** an "outbox" record (AdmitFlow: the draft's status becomes `approved`)
2. A separate worker reads the outbox and delivers (AdmitFlow: `admitflow send-approved`, run every minute by a scheduler)
3. The worker marks each delivered item (`sent`, with the provider's message ID)

The request stays fast; failures are retried; nothing is lost if the provider is down for an hour.

## Data contracts and mapping

Every integration is a mapping between two data models. Write it down:

| AdmitFlow | CRM property | Rule |
| --- | --- | --- |
| `email` | `email` | Lower-cased; the CRM's identifier |
| `name` | `firstname`, `lastname` | Split at the first space (imperfect; documented) |
| `status` | `admitflow_status` | Custom property, created by the CRM admin |
| `lead_id` | `admitflow_lead_id` | Lets marketing trace a contact back |

Custom properties must exist in the CRM before syncing. That's a request to the client's CRM admin, and a classic forgotten prerequisite.

## Check yourself

The website team says: "We can either call your webhook on every submission, or drop a CSV of the day's submissions in a bucket at midnight." Which would you choose for AdmitFlow, and would you want both? Justify it with freshness, failure behaviour and effort.

Next: [Lesson 03 — Webhooks done right](03-webhooks.md)
