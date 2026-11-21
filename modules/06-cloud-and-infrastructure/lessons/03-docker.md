# Lesson 03 — Docker

**Time:** ~6 hours · **Core**

## Why this matters

"It works on my laptop" happens because your laptop has a particular Python version, packages, OS and environment variables. A **container image** packages the application *with* everything it needs, so it runs the same way on your laptop, in CI, on the office VM and in the cloud. Almost every modern deployment target runs containers.

Install Docker Desktop (macOS/Windows) or Docker Engine (Linux): https://docs.docker.com/get-started/

## Images and containers

- **Image:** a read-only template (filesystem + metadata), built from a `Dockerfile`.
- **Container:** a running instance of an image, isolated from other processes.
- **Registry:** where images are stored and shared (Docker Hub, Artifact Registry, ECR, ACR).

```bash
docker run --rm -p 5432:5432 -e POSTGRES_PASSWORD=devpassword postgres:16-alpine
```

That downloads PostgreSQL and runs it, with nothing installed on your machine.

| Command | Does |
| --- | --- |
| `docker build -t admitflow-api .` | Build an image from the Dockerfile here |
| `docker run -p 8000:8000 -e KEY=value admitflow-api` | Run it, map a port, set env vars |
| `docker ps` / `docker ps -a` | Running / all containers |
| `docker logs -f <container>` | Follow its output |
| `docker exec -it <container> sh` | Open a shell inside it |
| `docker stop <container>` | Stop it |
| `docker images` / `docker image prune` | List / clean up images |

## The AdmitFlow Dockerfile, line by line

[`projects/admitflow/Dockerfile`](../../../projects/admitflow/Dockerfile):

```dockerfile
FROM python:3.12-slim AS build            # 1. start from an official, small base image
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY pyproject.toml ./                    # 2. copy only what's needed to install…
COPY admitflow/ admitflow/
RUN pip install ".[api,db]"               #    …so this slow layer is cached

FROM python:3.12-slim AS runtime          # 3. multi-stage: a fresh, clean final image
ENV PATH="/opt/venv/bin:$PATH" PYTHONUNBUFFERED=1 HOST=0.0.0.0 PORT=8000 TZ=Asia/Kolkata
WORKDIR /app
COPY --from=build /opt/venv /opt/venv     # 4. bring over only the installed packages
COPY alembic.ini ./
COPY migrations/ migrations/
RUN useradd --create-home --uid 10001 admitflow
USER admitflow                            # 5. don't run as root
EXPOSE 8000
HEALTHCHECK CMD python -c "…urlopen('http://127.0.0.1:8000/health')…"   # 6. Docker can tell if it's healthy
CMD ["admitflow", "serve"]                # 7. the default command
```

Key ideas:
1. **Layers and caching:** each instruction is a layer. Order from least to most frequently changing, so code edits don't reinstall dependencies.
2. **Multi-stage builds:** build tools stay in the build stage; the final image is smaller and has less to attack.
3. **Non-root user:** if the app is compromised, the attacker isn't root in the container.
4. **`HOST=0.0.0.0`:** inside a container, `127.0.0.1` means the container itself. A server listening there can't receive traffic forwarded from outside (this module's break & fix, problem #1).
5. **`PYTHONUNBUFFERED=1`:** logs appear immediately in `docker logs`.
6. **`TZ`:** AdmitFlow stores local time ([ADR-002](../../../projects/admitflow/docs/adr/002-local-time.md)), so the container's zone must be explicit.

## `.dockerignore`

Like `.gitignore`, for the build context. Keep out `.venv`, `.env` (secrets!), test data, `node_modules`. Smaller, faster, safer builds.

## The dashboard image

[`web/Dockerfile`](../../../projects/admitflow/web/Dockerfile) builds static files with Node, then serves them from a tiny nginx image. Node isn't in the final image at all. Note that `VITE_API_URL` is baked in **at build time**, so you build one dashboard image per environment (or serve a runtime config file; a common improvement).

## Image hygiene

- Pin base image versions (`python:3.12-slim`, not `python:latest`).
- Rebuild regularly to pick up security patches; scan images (`docker scout`, Trivy, or your registry's scanner).
- **Never put secrets in images.** Anyone who can pull the image can read every layer. Pass secrets at runtime.
- Build for the platform you run on. Apple-silicon laptops build `arm64` images by default; many servers are `amd64`. Use `docker build --platform linux/amd64 …`, or build in CI or the cloud.

## Check yourself

Write a Dockerfile for the Module 04 course-catalogue service ([Exercise 01](../exercises/01-dockerfile.md)). Build it, run it, and check `curl localhost:8000/courses` works, then check that the container runs as a non-root user (`docker exec <id> whoami`).

Next: [Lesson 04 — Docker Compose](04-docker-compose.md)
