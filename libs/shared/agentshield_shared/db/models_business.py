"""Business-domain models: the synthetic e-commerce system of record.

These tables are owned (migrated) by services/api's Alembic history but are
read and written by services/tool_server's MCP tools, which is why they
live in the shared package both services depend on.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agentshield_shared.db.base import Base, new_id, utc_now


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    customer_key: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email_hash: Mapped[str] = mapped_column(String, nullable=False)
    tier: Mapped[str] = mapped_column(String, nullable=False, default="standard")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    orders: Mapped[list["Order"]] = relationship(back_populates="customer")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), nullable=False)
    order_number: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="placed")
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="USD")
    items: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    customer: Mapped["Customer"] = relationship(back_populates="orders")
    shipments: Mapped[list["Shipment"]] = relationship(back_populates="order")


class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), nullable=False)
    carrier: Mapped[str] = mapped_column(String, nullable=False)
    tracking_number: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="label_created")
    eta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    history: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    order: Mapped["Order"] = relationship(back_populates="shipments")


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    policy_key: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(nullable=False, default=1)
    tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
