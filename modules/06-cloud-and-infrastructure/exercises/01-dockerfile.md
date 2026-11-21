# Exercise 01 — Containerize the course-catalogue service

Take your Module 04 course-catalogue service (or the [reference](../../04-software-engineering/exercises/solutions/course_service.py)) and write a `Dockerfile` that:

1. Uses a pinned, slim Python base image
2. Installs dependencies in a layer that's cached when only code changes
3. Runs as a **non-root** user
4. Listens on `0.0.0.0` and the port in `$PORT` (default 8000)
5. Has a `HEALTHCHECK`
6. Contains **no secrets**: `ADMIN_TOKEN` is supplied at `docker run` time
7. Has a `.dockerignore`

Then:
```bash
docker build -t course-service .
```
```bash
docker run --rm -p 8000:8000 -e ADMIN_TOKEN=local-test-token course-service
```
```bash
curl localhost:8000/courses
```

Check: `docker image ls course-service` (size), `docker run --rm course-service whoami` (not root), and `docker history course-service` (no secrets in any layer).
