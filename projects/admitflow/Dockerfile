# AdmitFlow API image (Module 06).
# Build:  docker build -t admitflow-api .
# Run:    docker run -p 8000:8000 -e ADMITFLOW_SECRET_KEY=... -e DATABASE_URL=... admitflow-api

# ---- build stage: install dependencies into a virtual environment ----
FROM python:3.12-slim AS build
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
# Copy only what's needed to install first, so this layer is cached when only code changes
COPY pyproject.toml ./
COPY admitflow/ admitflow/
RUN pip install ".[api,db]"

# ---- runtime stage: small image, no compilers, non-root user ----
FROM python:3.12-slim AS runtime
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    TZ=Asia/Kolkata
WORKDIR /app
COPY --from=build /opt/venv /opt/venv
COPY alembic.ini ./
COPY migrations/ migrations/
RUN useradd --create-home --uid 10001 admitflow
USER admitflow
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
  CMD python -c "import urllib.request,os; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/health', timeout=2)" || exit 1
CMD ["admitflow", "serve"]
