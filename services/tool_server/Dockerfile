FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /workspace
COPY pyproject.toml uv.lock ./
COPY libs/shared libs/shared
COPY services/tool_server services/tool_server

RUN uv sync --package agentshield-tool-server

CMD ["uv", "run", "--package", "agentshield-tool-server", "uvicorn", "agentshield_tools.server:app", "--host", "0.0.0.0", "--port", "9000"]
