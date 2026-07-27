#!/usr/bin/env python
"""CLI entrypoint: `uv run --project services/api python ../../scripts/seed.py`
(or, from the repo root, `uv run --package agentshield-api python scripts/seed.py`)."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from agentshield.core.config import get_settings  # noqa: E402
from agentshield.seed import run_seed  # noqa: E402


def main() -> None:
    settings = get_settings()
    dataset_dir = REPO_ROOT / "dataset"
    summary = run_seed(settings.database_url, dataset_dir, pinecone_api_key=settings.pinecone_api_key)
    print(f"Seeded: {summary}")


if __name__ == "__main__":
    main()
