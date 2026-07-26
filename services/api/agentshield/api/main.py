"""FastAPI application entrypoint for the AgentShield API service."""

from fastapi import FastAPI

app = FastAPI(title="AgentShield API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
