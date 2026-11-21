# Coding practice: FDE-flavoured problems

Each takes 20–40 minutes. Say your approach and its complexity **before** coding; test with edge cases **after**. Solutions (with checks): [`solutions/coding_solutions.py`](solutions/coding_solutions.py).

1. **Merge duplicate customers.** Given records with `id`, `email` and `phone`, two records are the same customer if they share an email **or** a phone (transitively). Return groups of IDs. *(Hint: union-find.)*
2. **Busy calendar.** Given counsellors' booked intervals `(start, end)` in minutes, return the free slots of at least 30 minutes between 9:00 and 18:00.
3. **Top channels.** Given a stream of enquiry events `(timestamp, channel)`, return the top-k channels in the last 24 hours at any query time. Discuss memory.
4. **Validate a CSV row.** Given a header and rows as strings, return valid rows as dicts and invalid ones with reasons (wrong column count, bad date, missing required field). Handle quoted commas.
5. **Rate limiter.** Implement a token bucket with `allow(key, now)`. Then discuss making it work across several servers.
6. **LRU cache.** `get` and `put` in O(1), with capacity. Then: how would you cache LLM answers, and when must the cache be invalidated?
7. **Diff two exports.** Given yesterday's and today's exports (lists of dicts keyed by `id`), return added, removed and changed records with the changed fields.
8. **Retry with backoff.** Write `call_with_retry(fn, attempts, base_delay, retry_on)` with exponential backoff and jitter; injectable `sleep` for testing.
