# ============================================================================
# AI Engineering Operating System — Dockerfile
# Multi-stage build: Python 3.12 slim
# ============================================================================

# ---------------------------------------------------------------------------
# Stage 1 — Builder (installs package + dev dependencies)
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ src/

RUN pip install --no-cache-dir -e ".[dev]"

# ---------------------------------------------------------------------------
# Stage 2 — Runtime
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy project files
COPY . .

# Install package in runtime (editable so tests discover it)
RUN pip install --no-cache-dir -e ".[dev]"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["pytest"]
CMD ["-v", "--tb=short"]
