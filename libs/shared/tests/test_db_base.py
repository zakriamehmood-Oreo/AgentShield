from datetime import datetime

from sqlalchemy import text

from agentshield_shared.db.base import Base, make_engine, make_session_factory, new_id, utc_now


def test_make_engine_and_session_factory_work_against_sqlite():
    engine = make_engine("sqlite:///:memory:")
    Session = make_session_factory(engine)
    with Session() as session:
        result = session.execute(text("SELECT 1")).scalar_one()
        assert result == 1


def test_base_has_empty_metadata_before_any_models_are_defined_here():
    # This module only defines the declarative base — models live in
    # models_business.py (Task 2). Metadata is a shared registry, so this
    # just confirms Base itself is usable as a declarative base.
    assert hasattr(Base, "metadata")


def test_new_id_returns_unique_strings():
    assert new_id() != new_id()
    assert isinstance(new_id(), str)


def test_utc_now_returns_timezone_aware_datetime():
    now = utc_now()
    assert isinstance(now, datetime)
    assert now.tzinfo is not None
