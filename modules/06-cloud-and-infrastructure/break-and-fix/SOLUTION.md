# Break & Fix — Solution

> ⚠️ Try it properly first.

| # | Symptom | Root cause | Fix | Prevention |
| --- | --- | --- | --- | --- |
| 1 | `Uvicorn running on http://127.0.0.1:8000` + `Recv failure: Connection reset by peer` | The server listens on the container's **loopback** only. Docker's port mapping forwards traffic to the container's network interface, where nothing listens | `--host 0.0.0.0` (or use the image's default `CMD ["admitflow", "serve"]`, which reads `HOST=0.0.0.0`) | Bake container-correct defaults into the image; smoke-test the image in CI (`curl /health` against `docker run`) |
| 2 | `/ready` → 503; log: `connection to server at "127.0.0.1", port 5432 failed: Connection refused` | `DATABASE_URL` points to `localhost`, which, inside the api container, is the api container | Use the Compose service name: `@db:5432` | Readiness endpoint that checks the database (it caught this); never copy laptop URLs into deployment config |
| 3 | Browser: `blocked by CORS policy … No 'Access-Control-Allow-Origin' header` | `ADMITFLOW_CORS_ORIGINS` is the **developer's** origin (`http://localhost:5173`), not the real dashboard origin `http://10.20.0.15:8080` | `ADMITFLOW_CORS_ORIGINS: http://10.20.0.15:8080` | Per-environment config files; a post-deploy check that logs in through the real dashboard |
| 4 | Login → 500; `RuntimeError: ADMITFLOW_SECRET_KEY must be set…` | The required secret was never configured | Set it from `.env` (`${ADMITFLOW_SECRET_KEY:?…}`), generated randomly, never committed | Make Compose **refuse to start** when it's missing (`:?` syntax); in the cloud, use a secret manager |

Also worth fixing: no `migrate` step (tables would be missing on a fresh database), no database health check (`depends_on` without `condition` only waits for the container to *start*, not for PostgreSQL to accept connections), and the database has no volume, so **all data would be lost when the container is recreated**. That last one is the most dangerous issue in the file, even though it isn't causing today's symptoms.

## Corrected file

The reference [`projects/admitflow/docker-compose.yml`](../../../projects/admitflow/docker-compose.yml) fixes all of these, with the CORS origin changed for this VM:

```yaml
  api:
    build: .
    environment:
      DATABASE_URL: postgresql+psycopg://admitflow:${POSTGRES_PASSWORD}@db:5432/admitflow
      ADMITFLOW_SECRET_KEY: ${ADMITFLOW_SECRET_KEY:?set ADMITFLOW_SECRET_KEY in .env}
      ADMITFLOW_CORS_ORIGINS: http://10.20.0.15:8080
    ports: ["8000:8000"]
    depends_on:
      migrate:
        condition: service_completed_successfully
```

## Go-live checklist that would have caught all four

- [ ] `curl http://<server>:8000/health` from **another machine** returns ok (#1)
- [ ] `curl http://<server>:8000/ready` returns ready (#2)
- [ ] Log in through the **real dashboard URL** in a browser with dev tools open (#3, #4)
- [ ] Every required variable is listed in `.env.example` and enforced with `:?` (#4)
- [ ] Database on a named volume; backup and restore tested
- [ ] Containers restart automatically (`restart: unless-stopped`) after a VM reboot

## Message to Mr. Fernandes

> The system was set up with settings from the engineer's laptop, so the server wasn't reachable, couldn't find its database, and blocked logins from the office network. I've corrected all four settings and tested logging in from a counsellor's browser. Counsellors can log in now. I also found that data wasn't being saved permanently, which is now fixed, with a daily backup. I'll be on site Monday morning for the start of the pilot.
