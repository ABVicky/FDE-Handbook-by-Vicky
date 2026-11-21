# Lesson 14 — Calling HTTP APIs

**Time:** ~3 hours · **Core**

## Why this matters

Integrations are API calls: to the client's CRM, a messaging provider, an LLM. In Module 02 you made requests with `curl`. Now you'll make them from code, and handle the failures that are guaranteed to happen in production.

## A first request with httpx

[httpx](https://www.python-httpx.org/) is a modern HTTP client (the older, also very common [requests](https://requests.readthedocs.io/) library works almost identically).

```bash
python -m pip install httpx
```

```python
import httpx

response = httpx.get("https://api.github.com/repos/python/cpython", timeout=10)
response.raise_for_status()          # raises an exception for 4xx/5xx
data = response.json()               # parse the JSON body into dicts/lists
print(data["full_name"], data["stargazers_count"])
```

## Sending data, headers and query parameters

```python
response = httpx.post(
    "https://crm.example/api/contacts",
    json={"name": "Zoë Müller", "email": "zoe@example.org"},   # sent as JSON
    headers={"Authorization": f"Bearer {api_key}"},
    params={"dedupe": "true"},                                 # → ?dedupe=true
    timeout=10,
)
```

**Never hard-code API keys.** Read them from environment variables (Module 02, Lesson 04):

```python
import os
api_key = os.environ["CRM_API_KEY"]
```

## Always set a timeout

Without a timeout, a request to a stuck server can hang your program forever. Every call in production code needs one.

## Handling failures

| Problem | Example | What to do |
| --- | --- | --- |
| Network error / timeout | `httpx.ConnectError`, `httpx.TimeoutException` | Retry a few times with backoff |
| `429 Too Many Requests` | Rate limit | Wait (use `Retry-After` if given), then retry |
| `5xx` | Server error | Retry with backoff; give up after a few attempts |
| `4xx` (except 429) | Bad request, auth problem | **Don't retry**: fix the request; log the response body |

A simple retry with exponential backoff:

```python
import time
import httpx

RETRYABLE = {429, 500, 502, 503, 504}

def get_with_retry(url, attempts=4, **kwargs):
    for attempt in range(attempts):
        try:
            response = httpx.get(url, timeout=10, **kwargs)
            if response.status_code not in RETRYABLE:
                response.raise_for_status()
                return response.json()
        except (httpx.TimeoutException, httpx.ConnectError):
            if attempt == attempts - 1:
                raise
        wait = 2 ** attempt               # 1, 2, 4, 8 seconds
        time.sleep(wait)
    raise RuntimeError(f"gave up after {attempts} attempts: {url}")
```

(In production you'd also add random "jitter" to the wait, and respect `Retry-After`. Libraries such as `tenacity` do this well.)

## Pagination

APIs rarely return everything at once:

```python
def all_contacts(client):
    page = 1
    while True:
        batch = client.get("/contacts", params={"page": page, "per_page": 100}).json()
        if not batch:
            break
        yield from batch
        page += 1
```

Different APIs paginate differently (page numbers, cursors, `next` links). Read the docs.

## Testing code that calls APIs

Don't call real APIs in unit tests: they're slow, flaky and may cost money. Put the HTTP call in one small function and replace it in tests (`monkeypatch`), or use `httpx.MockTransport`. You'll see this in Exercise set 05.

## Without any library

On a locked-down client machine you may not be able to install packages. The standard library can do basic requests:

```python
import json
from urllib.request import Request, urlopen

with urlopen(Request("https://api.github.com/zen", headers={"User-Agent": "fde-handbook"}), timeout=10) as r:
    print(r.read().decode())
```

## Check yourself

Write `fetch_json(url)` that returns the parsed JSON, retries up to 3 times on timeouts and 5xx responses, does **not** retry on 404, and logs each retry at WARNING level.

Next: [Lesson 15 — Async basics](15-async-basics.md)
