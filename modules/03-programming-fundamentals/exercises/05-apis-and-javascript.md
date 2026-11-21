# Exercise set 05 — APIs and JavaScript

## Part A: a robust API call (Python)

1. Write **`fetch_json(url, client=None, attempts=3, sleep=time.sleep)`** using `httpx`:
   - returns parsed JSON on success
   - retries on timeouts and on status 429, 500, 502, 503, 504, waiting 1 s, 2 s, 4 s… between attempts
   - does **not** retry on other 4xx (raise immediately)
   - raises after the final failed attempt
   - logs each retry at WARNING level

   The `client` and `sleep` parameters exist so tests can replace the network and the waiting ("dependency injection").
2. Test it **without the internet** using `httpx.MockTransport`, which lets you decide what each request returns:
   ```python
   responses = iter([httpx.Response(503), httpx.Response(200, json={"ok": True})])
   transport = httpx.MockTransport(lambda request: next(responses))
   client = httpx.Client(transport=transport)
   ```
   Cover: success first time; one 503 then success; 404 (no retry); always 503 (gives up after 3).
3. Try it for real: `fetch_json("https://api.github.com/repos/python/cpython")` and print the star count.

## Part B: JavaScript and TypeScript

4. Create a store with the AdmitFlow CLI (see the [build](../build.md)), so you have `leads.json`.
5. Write **`stats.mjs`** (Node.js) that reads `leads.json` and prints leads per course, highest first, and the number of leads that came through more than one channel.
   ```bash
   node stats.mjs path/to/leads.json
   ```
6. Convert it to **`stats.ts`** with a `Lead` interface, run it with `npx tsx stats.ts`, and check it with `npx tsc --noEmit --strict stats.ts`.
