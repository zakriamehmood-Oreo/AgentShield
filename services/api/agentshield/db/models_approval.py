"""Human-approval lifecycle and the immutable, hash-chained audit log.

AuditLog is append-only by convention (no code path in this codebase issues
an UPDATE or DELETE against it): each row's `hash` commits to its own
payload plus the previous row's hash, so any row tampered with after the
fact breaks the chain for every row after it.
"""

import hashlib
import json
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from agentshield_shared.db.base import Base, new_id, utc_now


def compute_next_hash(prev_hash: str | None, payload: dict) -> str:
    canonical_payload = json.dumps(payload, sort_keys=True, default=str)
    digest_input = f"{prev_hash or ''}|{canonical_payload}".encode("utf-8")
    return hashlib.sha256(digest_input).hexdigest()


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    tool_call_id: Mapped[str] = mapped_column(ForeignKey("tool_calls.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")  # pending | approved | rejected
    reviewer: Mapped[str | None] = mapped_column(String, nullable=True)
    decision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    entity_id: Mapped[str] = mapped_column(String, nullable=False)
    actor: Mapped[str] = mapped_column(String, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    prev_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    hash: Mapped[str] = mapped_column(String, nullable=False)
