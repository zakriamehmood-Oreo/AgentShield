FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /workspace
COPY pyproject.toml uv.lock ./
COPY libs/shared libs/shared
COPY services/api services/api

RUN uv sync --package agentshield-api

CMD ["uv", "run", "--package", "agentshield-api", "uvicorn", "agentshield.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
