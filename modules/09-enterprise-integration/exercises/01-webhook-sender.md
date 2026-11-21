# Exercise 01 — Play the website: send signed webhooks

Write `webhook_sender.py` that acts as the website's server and sends form submissions to AdmitFlow's `/public/webhooks/website-form`:

1. Five valid submissions, each signed (HMAC-SHA256 over `"{timestamp}." + body`) with a unique event ID
2. One of them **sent twice** → expect `{"status": "duplicate"}`
3. One with the body **changed after signing** → expect `401`
4. One with a **timestamp 10 minutes old** → expect `401`
5. One with no email and no phone → expect `422`

Check the resulting leads. Run it against AdmitFlow in-process (`TestClient(create_app(repo))`), then against a running server (`admitflow serve` with `ADMITFLOW_WEBHOOK_SECRET` set).
