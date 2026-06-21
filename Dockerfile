# syntax=docker/dockerfile:1
# qchem-stack images: build with --target slim (default) or --target full
# Note: CI and release gates use Python 3.12; images currently track 3.11-slim for size.
# Align to 3.12 when rebuilding base images for production (pyproject requires >=3.10).

FROM python:3.11-slim AS builder-base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README_PYPI.md README.md ./
COPY src ./src

FROM builder-base AS builder-slim

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir ".[chem,quantum,api]"

FROM builder-base AS builder-full

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir ".[all]"

FROM python:3.11-slim AS runtime-base

WORKDIR /app

RUN useradd -m -u 1000 qchem

FROM runtime-base AS slim

COPY --from=builder-slim /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder-slim /usr/local/bin /usr/local/bin
COPY pyproject.toml README_PYPI.md README.md ./
COPY src ./src
COPY configs ./configs

RUN chown -R qchem:qchem /app

USER qchem

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import qchem_stack; print('OK')" || exit 1

CMD ["qchem-jobs-worker", "--db", "/data/jobs.sqlite"]

FROM slim AS full

USER root
COPY --from=builder-full /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder-full /usr/local/bin /usr/local/bin
RUN chown -R qchem:qchem /app
USER qchem
