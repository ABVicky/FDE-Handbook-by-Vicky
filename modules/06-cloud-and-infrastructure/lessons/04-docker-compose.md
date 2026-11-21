# Lesson 04 — Docker Compose

**Time:** ~3 hours · **Core**

## Why this matters

AdmitFlow is four things: a database, a migration step, an API and a dashboard. Compose describes them in one file and starts them with one command. That gives every developer (and the office VM) an identical environment, and it's often exactly how a small client runs production on a single server.

## The AdmitFlow Compose file

[`projects/admitflow/docker-compose.yml`](../../../projects/admitflow/docker-compose.yml):

```yaml
services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: admitflow
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?set POSTGRES_PASSWORD in .env}   # refuse to start without it
      POSTGRES_DB: admitflow
    volumes:
      - pgdata:/var/lib/postgresql/data      # data survives container re-creation
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admitflow"]
    ports:
      - "127.0.0.1:5432:5432"                # reachable from this machine only

  migrate:
    build: .
    command: ["alembic", "upgrade", "head"]
    environment:
      DATABASE_URL: postgresql+psycopg://admitflow:${POSTGRES_PASSWORD}@db:5432/admitflow
    depends_on:
      db: { condition: service_healthy }      # wait until PostgreSQL accepts connections

  api:
    build: .
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql+psycopg://admitflow:${POSTGRES_PASSWORD}@db:5432/admitflow
      ADMITFLOW_SECRET_KEY: ${ADMITFLOW_SECRET_KEY:?set ADMITFLOW_SECRET_KEY in .env}
      ADMITFLOW_CORS_ORIGINS: http://localhost:8080
    ports: ["8000:8000"]
    depends_on:
      migrate: { condition: service_completed_successfully }   # never start against an old schema

  web:
    build: { context: web, args: { VITE_API_URL: http://localhost:8000 } }
    ports: ["8080:8080"]

volumes:
  pgdata:
```

## Networking inside Compose

Compose creates a private network where **each service is reachable by its name**. The api connects to `db:5432`, not `localhost:5432`, because inside the api container, `localhost` is the api container itself (break & fix problem #2).

`ports: ["8000:8000"]` publishes a container port on the host (`host:container`). Services talk to each other on the private network without publishing anything. Publish only what users need; bind admin-only ports to `127.0.0.1:`.

## Startup order and readiness

`depends_on` alone only waits for a container to **start**, not to be **ready**. Use health checks and conditions (`service_healthy`, `service_completed_successfully`). Your app should also retry its database connection at startup, because in the cloud there's no Compose to order things for you.

## Secrets and `.env`

Compose reads `${VARIABLES}` from a `.env` file next to the Compose file:

```bash
cp .env.example .env
```

Commit `.env.example` with placeholders, never `.env`. The `${VAR:?message}` syntax makes Compose refuse to start with a clear message if a required secret is missing, which is better than a 500 error on the first login (break & fix problem #4).

## Everyday commands

```bash
docker compose up --build -d        # build and start everything in the background
```

```bash
docker compose ps                   # status, including health
```

```bash
docker compose logs -f api          # follow one service's logs
```

```bash
docker compose run --rm api admitflow create-user priya --full-name "Priya Nair"   # one-off command
```

```bash
docker compose down                 # stop and remove containers (the volume, and your data, remain)
```

`docker compose down -v` also deletes volumes, **including the database**. Never run it on a server with real data.

## Compose in production?

For a single-server deployment at a small client, Compose with `restart: unless-stopped`, a volume, backups, and a reverse proxy for HTTPS (Caddy or nginx) is a reasonable, maintainable choice. When you need several servers, automatic scaling, or zero-downtime deploys, move to a managed container platform (Lesson 06) or Kubernetes (Lesson 08).

## Check yourself

Do the [break & fix](../break-and-fix/README.md). Then explain what would happen to the database's data in the *original* handover file if someone ran `docker compose down && docker compose up`.

Next: [Lesson 05 — CI/CD with GitHub Actions](05-ci-cd.md)
