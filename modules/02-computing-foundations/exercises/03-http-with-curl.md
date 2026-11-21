# Exercise 03 — Talk HTTP with curl

## Part A: a public website

1. Fetch `https://example.com` and print only the **status code**.
2. Fetch it again with `-v`. Find and write down: the IP address curl connected to, the TLS version, and the `Content-Type` of the response.
3. Request `https://example.com/this-does-not-exist`. What status code comes back?
4. Request `http://github.com` (note: **http**, not https) with `-i`. What status code do you get, and what does the `Location` header say? Why does the site do this?

## Part B: your own server

In terminal 1, in `projects/admitflow/data`:

```bash
python3 -m http.server 8000
```

In terminal 2:

5. Request `http://localhost:8000/`. What does the body contain?
6. Download `leads_sample.csv` through the server into `/tmp/downloaded.csv` (`curl -o`). Check it's identical to the original with `diff`.
7. Send a `POST` request to `http://localhost:8000/`. What status code comes back, and what does terminal 1 print? Why?
8. Stop the server (<kbd>Ctrl</kbd>+<kbd>C</kbd> in terminal 1) and request `http://localhost:8000/` again. What exact error do you get? Which category from Lesson 05 is it?

## Part C: explain it

9. In your own words, write the life of the request in step 5, from pressing Enter to seeing the output. Mention: localhost, port, TCP, HTTP method, status code.
