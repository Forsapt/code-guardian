FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM aquasec/trivy:latest AS trivy

FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends git graphviz \
    && rm -rf /var/lib/apt/lists/*

COPY --from=trivy /usr/local/bin/trivy /usr/local/bin/trivy
COPY --from=builder /app/.venv /app/.venv
COPY code_guardian/ /app/code_guardian/

ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app

ENTRYPOINT ["python", "-m", "code_guardian.cli"]
