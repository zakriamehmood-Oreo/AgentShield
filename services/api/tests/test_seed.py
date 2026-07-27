"""Integration test — requires `docker compose up -d db` running locally
on localhost:5433 (see Task 7)."""

from pathlib import Path

from sqlalchemy import create_engine, text

from agentshield.seed import run_seed
from agentshield_shared.db.base import Base

DATABASE_URL = "postgresql+psycopg://agentshield:change-me@localhost:5433/agentshield"
DATASET_DIR = Path(__file__).resolve().parents[3] / "dataset"


def _reset_database():
    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(text(f'TRUNCATE TABLE "{table.name}" CASCADE'))


def test_run_seed_populates_customers_orders_policies_and_scenarios():
    _reset_database()
    summary = run_seed(DATABASE_URL, DATASET_DIR, pinecone_api_key="")

    assert summary["customers"] > 0
    assert summary["orders"] > 0
    assert summary["policies"] == 5
    assert summary["scenarios"] == 100
    assert summary["pinecone_upserted"] == 0  # no key provided -> gracefully skipped

    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        order_count = conn.execute(text("SELECT COUNT(*) FROM orders")).scalar_one()
        assert order_count == summary["orders"]


def test_run_seed_is_idempotent_when_run_twice():
    _reset_database()
    first_summary = run_seed(DATABASE_URL, DATASET_DIR, pinecone_api_key="")
    second_summary = run_seed(DATABASE_URL, DATASET_DIR, pinecone_api_key="")
    assert first_summary == second_summary
