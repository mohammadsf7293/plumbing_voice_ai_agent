# Match local dependency resolution; model assets are downloaded at build time.
FROM ghcr.io/astral-sh/uv:0.8.15 AS uv
FROM python:3.11-slim-bookworm
ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"
WORKDIR /app
COPY --from=uv /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev
RUN useradd --create-home --home-dir /home/appuser --uid 10001 appuser
COPY agent.py ./
COPY plumbing ./plumbing
RUN chown -R appuser:appuser /app
USER appuser
RUN python agent.py download-files
CMD ["python", "agent.py", "start"]
