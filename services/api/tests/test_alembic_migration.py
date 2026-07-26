"""Verifies the Alembic migration actually created every expected table
against a real Postgres. Requires `docker compose up -d db` to be running
locally — this test is an integration test, not a unit test.
"""

from sqlalchemy import create_engine, inspect

DATABASE_URL = "postgresql+psycopg://agentshield:change-me@localhost:5433/agentshield"

EXPECTED_TABLES = {
    "customers", "orders", "shipments", "policies",
    "conversations", "messages", "spans", "tool_calls", "citations",
    "approval_requests", "audit_log",
    "agent_versions", "scenarios", "eval_runs", "eval_results", "regression_comparisons",
    "alembic_version",
}


def test_all_expected_tables_exist_after_migration():
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    actual_tables = set(inspector.get_table_names())
    missing = EXPECTED_TABLES - actual_tables
    assert not missing, f"Migration did not create: {missing}"
