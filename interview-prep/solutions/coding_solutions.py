"""Reference solutions for interview-prep/coding.md. Run: python coding_solutions.py (self-checking)."""
import csv
import io
import random
import time
from collections import Counter, OrderedDict, deque
from datetime import datetime


# 1. Merge duplicate customers (union-find) — O(n α(n))
def merge_customers(records):
    parent = {r["id"]: r["id"] for r in records}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]   # path halving
            x = parent[x]
        return x

    def union(a, b):
        parent[find(a)] = find(b)

    first_seen = {}
    for record in records:
        for key in ("email", "phone"):
            value = (record.get(key) or "").strip().lower()
            if value:
                if (key, value) in first_seen:
                    union(record["id"], first_seen[(key, value)])
                else:
                    first_seen[(key, value)] = record["id"]
    groups = {}
    for record in records:
        groups.setdefault(find(record["id"]), []).append(record["id"])
    return sorted(sorted(g) for g in groups.values())


# 2. Free slots — sort and sweep, O(n log n)
def free_slots(booked, day_start=9 * 60, day_end=18 * 60, minimum=30):
    slots, cursor = [], day_start
    for start, end in sorted(booked):
        if start - cursor >= minimum:
            slots.append((cursor, start))
        cursor = max(cursor, end)
    if day_end - cursor >= minimum:
        slots.append((cursor, day_end))
    return slots


# 3. Top channels in a sliding 24h window — deque + counter; memory O(events in window)
class TopChannels:
    WINDOW = 24 * 3600

    def __init__(self):
        self.events, self.counts = deque(), Counter()

    def add(self, timestamp, channel):
        self.events.append((timestamp, channel))
        self.counts[channel] += 1

    def top(self, k, now):
        while self.events and self.events[0][0] <= now - self.WINDOW:
            _, channel = self.events.popleft()
            self.counts[channel] -= 1
            if not self.counts[channel]:
                del self.counts[channel]
        return [c for c, _ in sorted(self.counts.items(), key=lambda kv: (-kv[1], kv[0]))[:k]]


# 4. Validate CSV rows
def validate_rows(text, required=("id", "date")):
    reader = csv.reader(io.StringIO(text))
    header = next(reader)
    valid, invalid = [], []
    for line_num, row in enumerate(reader, start=2):
        if len(row) != len(header):
            invalid.append((line_num, f"expected {len(header)} columns, got {len(row)}"))
            continue
        record = dict(zip(header, (cell.strip() for cell in row)))
        missing = [f for f in required if not record.get(f)]
        if missing:
            invalid.append((line_num, f"missing {', '.join(missing)}"))
            continue
        try:
            datetime.strptime(record["date"], "%Y-%m-%d")
        except ValueError:
            invalid.append((line_num, f"bad date {record['date']!r}"))
            continue
        valid.append(record)
    return valid, invalid


# 5. Token bucket
class TokenBucket:
    def __init__(self, rate_per_second, burst):
        self.rate, self.burst, self.buckets = rate_per_second, burst, {}

    def allow(self, key, now):
        tokens, last = self.buckets.get(key, (self.burst, now))
        tokens = min(self.burst, tokens + (now - last) * self.rate)
        allowed = tokens >= 1
        self.buckets[key] = (tokens - 1 if allowed else tokens, now)
        return allowed
    # Across servers: keep buckets in Redis with an atomic script, or rate-limit at the gateway.


# 6. LRU cache
class LRUCache:
    def __init__(self, capacity):
        self.capacity, self.data = capacity, OrderedDict()

    def get(self, key):
        if key not in self.data:
            return None
        self.data.move_to_end(key)
        return self.data[key]

    def put(self, key, value):
        self.data[key] = value
        self.data.move_to_end(key)
        if len(self.data) > self.capacity:
            self.data.popitem(last=False)
    # LLM answers: key on (normalized question, document-set version, model, prompt version);
    # invalidate whenever documents change (e.g. a new fee schedule).


# 7. Diff two exports
def diff_exports(old, new, key="id"):
    before, after = {r[key]: r for r in old}, {r[key]: r for r in new}
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    changed = {}
    for k in sorted(set(before) & set(after)):
        fields = {f: (before[k].get(f), after[k].get(f)) for f in set(before[k]) | set(after[k])
                  if before[k].get(f) != after[k].get(f)}
        if fields:
            changed[k] = fields
    return added, removed, changed


# 8. Retry with backoff and jitter
def call_with_retry(fn, attempts=4, base_delay=0.5, retry_on=(TimeoutError, ConnectionError), sleep=time.sleep,
                    rng=random.random):
    for attempt in range(attempts):
        try:
            return fn()
        except retry_on:
            if attempt == attempts - 1:
                raise
            sleep(base_delay * (2 ** attempt) * (0.5 + rng()))   # "equal jitter": 50–150% of the backoff


if __name__ == "__main__":
    records = [{"id": 1, "email": "a@x.com"}, {"id": 2, "phone": "555"}, {"id": 3, "email": "A@x.com", "phone": "555"},
               {"id": 4, "email": "b@x.com"}]
    assert merge_customers(records) == [[1, 2, 3], [4]]

    assert free_slots([(9 * 60, 10 * 60), (10 * 60 + 15, 12 * 60), (11 * 60, 13 * 60)]) == [(780, 1080)]
    assert free_slots([]) == [(540, 1080)]

    tc = TopChannels()
    for t, ch in [(0, "ad"), (10, "ad"), (20, "web"), (90000, "web"), (90001, "phone")]:
        tc.add(t, ch)
    assert tc.top(2, now=90002) == ["phone", "web"]       # the early "ad" events have expired

    text = 'id,name,date\n1,"Lee, Chloe",2026-09-01\n2,Omar\n3,Zoe,01/09/2026\n,Kai,2026-09-02\n'
    valid, invalid = validate_rows(text)
    assert [r["name"] for r in valid] == ["Lee, Chloe"] and [line for line, _ in invalid] == [3, 4, 5]

    bucket = TokenBucket(rate_per_second=1, burst=2)
    assert [bucket.allow("k", 0), bucket.allow("k", 0), bucket.allow("k", 0), bucket.allow("k", 1.0)] == [True, True, False, True]

    cache = LRUCache(2)
    cache.put("a", 1); cache.put("b", 2); cache.get("a"); cache.put("c", 3)
    assert cache.get("b") is None and cache.get("a") == 1

    added, removed, changed = diff_exports([{"id": 1, "s": "new"}, {"id": 2}], [{"id": 1, "s": "won"}, {"id": 3}])
    assert (added, removed, changed) == ([3], [2], {1: {"s": ("new", "won")}})

    calls, waits = [], []
    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise TimeoutError
        return "ok"
    assert call_with_retry(flaky, sleep=waits.append, rng=lambda: 0.5) == "ok" and waits == [0.5, 1.0]
    print("all checks passed")
