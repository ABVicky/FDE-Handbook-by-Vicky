# Lesson 07 — NoSQL and caching

**Time:** ~2 hours · **Core** (concepts) / *Stretch* (hands-on)

## Why this matters

Clients will have MongoDB, Redis, DynamoDB, Elasticsearch… and opinions about them. You need to know what each kind is good at, so you can integrate with them and push back when someone proposes the wrong tool.

## The main families

| Kind | Examples | Data shape | Good at | Weak at |
| --- | --- | --- | --- | --- |
| **Relational** | PostgreSQL, MySQL, SQL Server | Tables with relationships | Consistency, joins, ad-hoc questions | Huge write volumes across many machines |
| **Document** | MongoDB, Firestore, Cosmos DB | JSON-like documents | Flexible, nested records; one-record reads | Joins; cross-document consistency |
| **Key-value** | Redis, DynamoDB | Key → value | Extremely fast lookups, caching, counters | Querying by anything but the key |
| **Search** | Elasticsearch, OpenSearch | Indexed documents | Full-text search, relevance ranking | Being the source of truth |
| **Vector** | pgvector, Qdrant, Pinecone | Embeddings | Similarity search for AI (Module 08) | Everything else |
| **Wide-column / time-series** | Cassandra, TimescaleDB, InfluxDB | Rows by time/partition | Massive append-heavy data | Ad-hoc joins |

## A sensible default

**Start with PostgreSQL.** It's relational, handles JSON columns (`JSONB`), full-text search, and vector search (`pgvector`) well enough for most FDE projects. One database is one thing for the client's IT team to back up, secure and understand. Add a specialized store when you can name the specific problem it solves.

## Documents in a relational database

```sql
-- PostgreSQL: store the raw ad-platform payload alongside the clean columns
ALTER TABLE leads ADD COLUMN raw_payload JSONB;
SELECT raw_payload->>'campaign_name' FROM leads WHERE raw_payload @> '{"platform": "meta"}';
```

Keeping the raw record lets you re-process it later without asking the client for the export again.

## Caching with Redis

A **cache** keeps the result of expensive work so the next request is fast:

```python
import json
import redis

cache = redis.Redis.from_url("redis://localhost:6379/0")

def stats(repo):
    cached = cache.get("stats:v1")
    if cached:
        return json.loads(cached)
    result = compute_stats(repo)                       # slow: scans all leads
    cache.setex("stats:v1", 300, json.dumps(result))   # keep for 5 minutes
    return result
```

The hard part of caching is **invalidation**: when the data changes, the cache is stale. Choose a short expiry the business can accept ("stats up to 5 minutes old"), or delete the key when the data changes. Don't cache until you've measured a real problem.

Redis is also common for: rate-limiting counters (Module 10), background job queues, and session storage.

## Check yourself

The director wants a dashboard tile showing "leads received today," refreshed every time anyone loads the page, by 50 users. Would you cache it? For how long? What would you tell the director about how fresh the number is?

Next: [Lesson 08 — The modern data stack and data governance](08-data-stack-and-governance.md)
