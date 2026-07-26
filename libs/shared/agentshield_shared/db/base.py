"""Shared SQLAlchemy declarative base and engine/session factories.

Both services/api and services/tool_server import Base from here so that
every table in the database is registered on one metadata object, which is
what lets services/api's single Alembic history manage the whole schema.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def make_engine(database_url: str, echo: bool = False) -> Engine:
    return create_engine(database_url, echo=echo, future=True)


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)


def new_id() -> str:
    """Default for every model's string-UUID primary key."""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Default for every model's created_at/timestamp column."""
    return datetime.now(timezone.utc)
