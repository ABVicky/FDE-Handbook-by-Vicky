"""Exercise set 05, part A — reference solution.

Needs httpx:  python -m pip install httpx
Run checks:   python3 ex05_fetch.py
"""
from __future__ import annotations

import logging
import time
from typing import Any, Callable, Optional

import httpx

log = logging.getLogger("fetch_json")
RETRYABLE = {429, 500, 502, 503, 504}


def fetch_json(
    url: str,
    client: Optional[httpx.Client] = None,
    attempts: int = 3,
    sleep: Callable[[float], None] = time.sleep,
) -> Any:
    client = client or httpx.Client(timeout=10)
    for attempt in range(1, attempts + 1):
        try:
            response = client.get(url)
        except httpx.TimeoutException as exc:
            problem = f"timeout ({exc})"
        else:
            if response.status_code not in RETRYABLE:
                response.raise_for_status()  # other 4xx/5xx: fail immediately
                return response.json()
            problem = f"HTTP {response.status_code}"
        if attempt == attempts:
            raise RuntimeError(f"gave up on {url} after {attempts} attempts: {problem}")
        wait = 2 ** (attempt - 1)
        log.warning("attempt %d/%d failed (%s); retrying in %ss", attempt, attempts, problem, wait)
        sleep(wait)


def _client(*responses):
    queue = iter(responses)

    def handler(request):
        item = next(queue)
        if isinstance(item, Exception):
            raise item
        return item

    return httpx.Client(transport=httpx.MockTransport(handler))


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    waits = []
    url = "https://api.example/leads"

    assert fetch_json(url, _client(httpx.Response(200, json={"ok": True})), sleep=waits.append) == {"ok": True}
    assert waits == []

    result = fetch_json(url, _client(httpx.Response(503), httpx.Response(200, json=[1])), sleep=waits.append)
    assert result == [1] and waits == [1]

    try:
        fetch_json(url, _client(httpx.Response(404)), sleep=waits.append)
        raise AssertionError("expected HTTPStatusError")
    except httpx.HTTPStatusError:
        assert waits == [1]  # no extra wait: 404 is not retried

    waits.clear()
    try:
        fetch_json(url, _client(*[httpx.Response(503)] * 3), sleep=waits.append)
        raise AssertionError("expected RuntimeError")
    except RuntimeError as exc:
        assert "after 3 attempts" in str(exc) and waits == [1, 2]

    timeout = httpx.ReadTimeout("slow", request=httpx.Request("GET", url))
    assert fetch_json(url, _client(timeout, httpx.Response(200, json={})), sleep=lambda s: None) == {}
    print("all checks passed")
