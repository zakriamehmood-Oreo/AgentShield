from datetime import datetime

from sqlalchemy import MetaData, text
from sqlalchemy.orm import DeclarativeBase

from agentshield_shared.db.base import Base, make_engine, make_session_factory, new_id, utc_now


def test_make_engine_and_session_factory_work_against_sqlite():
    engine = make_engine("sqlite:///:memory:")
    Session = make_session_factory(engine)
    with Session() as session:
        result = session.execute(text("SELECT 1")).scalar_one()
        assert result == 1


def test_base_is_a_working_declarative_base():
    assert issubclass(Base, DeclarativeBase)
    assert isinstance(Base.metadata, MetaData)
    # create_all against a fresh engine must not raise, regardless of how
    # many tables other modules have registered on Base.metadata by the
    # time this runs — this is what actually proves Base works as a
    # declarative base, without any fragile "metadata is empty" premise.
    engine = make_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)


def test_new_id_returns_unique_strings():
    assert new_id() != new_id()
    assert isinstance(new_id(), str)


def test_utc_now_returns_timezone_aware_datetime():
    now = utc_now()
    assert isinstance(now, datetime)
    assert now.tzinfo is not None
