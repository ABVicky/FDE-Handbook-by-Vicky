# Exercise 01 — reference Dockerfile for the course-catalogue service.
# Put this next to course_service.py (with requirements.txt and .dockerignore).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000

WORKDIR /app

# Dependencies first: this layer is reused when only the code changes
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY course_service.py .

RUN useradd --create-home --uid 10001 app
USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/courses', timeout=2)" || exit 1

# Shell form so $PORT is expanded; exec replaces the shell so signals reach uvicorn
CMD exec uvicorn course_service:app --host 0.0.0.0 --port "$PORT"
