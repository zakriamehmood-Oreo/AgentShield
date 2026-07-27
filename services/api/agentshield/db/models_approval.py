"""Human-approval lifecycle and the immutable, hash-chained audit log.

Each `AuditLog` row's `hash` commits to that row's `entity_type`,
`entity_id`, `actor`, `action`, and `payload`, chained together with the
previous row's hash (`prev_hash`) via `compute_next_hash()`. That means any
row whose `entity_type`, `entity_id`, `actor`, `action`, or `payload` is
altered after the fact breaks the chain for every row after it — in
particular, `actor`/`action` (who did what) can't be silently rewritten
without detection.

What this does NOT cover yet: append-only enforcement. Nothing here stops
a caller (or an attacker with UPDATE/DELETE access on `audit_log`) from
rewriting a row *and* recomputing every subsequent hash to match, since the
hash chain only detects tampering, it doesn't prevent rewriting. Enforcing
true append-only-ness (e.g. a DB trigger rejecting UPDATE/DELETE, plus a
`verify_chain()` helper to detect breaks) is a known gap, tracked for M3,
not this fix.
"""

import hashlib
import json
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from agentshield_shared.db.base import Base, new_id, utc_now


def compute_next_hash(
    prev_hash: str | None,
    entity_type: str,
    entity_id: str,
    actor: str,
    action: str,
    payload: dict,
) -> str:
    # `created_at` is deliberately excluded: it's assigned by the ORM at
    # insert time via `utc_now()`, so covering it here would require
    # restructuring how rows get their timestamp. A future write path that
    # also wants tamper-evidence over the timestamp can pass an explicit
    # value through this same function later.
    entry = {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "actor": actor,
        "action": action,
        "payload": payload,
    }
    canonical_entry = json.dumps(entry, sort_keys=True, default=str)
    digest_input = f"{prev_hash or ''}|{canonical_entry}".encode("utf-8")
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
