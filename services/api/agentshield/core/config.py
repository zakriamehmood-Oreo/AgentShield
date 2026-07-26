"""Central environment-driven configuration for the API service.

Every value that could plausibly need to change between local dev, CI, and
production is read from the environment here — nowhere else in the codebase
should call os.environ directly for these settings.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://agentshield:change-me@localhost:5433/agentshield"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_eval_model: str = "gpt-4o-mini"

    pinecone_api_key: str = ""
    pinecone_index_name: str = "agentshield-policies"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"

    mock_mode: bool = True
    max_model_calls_per_run: int = 50
    max_concurrency: int = 4
    token_budget_usd_per_run: float = 1.00
    agent_max_steps: int = 8

    secret_key: str = "change-me"
    tool_server_url: str = "http://localhost:9000/mcp"


@lru_cache
def get_settings() -> Settings:
    return Settings()
