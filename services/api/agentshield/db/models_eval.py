"""Prompt/agent versioning and evaluation result storage.

Scenario rows mirror the version-controlled YAML files under dataset/ — the
files are the source of truth; this table exists so eval_results can join
against scenario metadata (category, forbidden_actions, etc.) in SQL.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from agentshield_shared.db.base import Base, new_id, utc_now


class AgentVersion(Base):
    __tablename__ = "agent_versions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    external_key: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    user_identity: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    customer_message: Mapped[str] = mapped_column(Text, nullable=False)
    account_state: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    expected_action: Mapped[str] = mapped_column(String, nullable=False)
    allowed_tools: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    forbidden_actions: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    expected_policy_citations: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    requires_human_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    version: Mapped[int] = mapped_column(nullable=False, default=1)


class EvalRun(Base):
    __tablename__ = "eval_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    dataset_version: Mapped[str] = mapped_column(String, nullable=False)
    agent_version_id: Mapped[str] = mapped_column(ForeignKey("agent_versions.id"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)


class EvalResult(Base):
    __tablename__ = "eval_results"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    eval_run_id: Mapped[str] = mapped_column(ForeignKey("eval_runs.id"), nullable=False)
    scenario_id: Mapped[str] = mapped_column(ForeignKey("scenarios.id"), nullable=False)
    metric_name: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[float] = mapped_column(nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)


class RegressionComparison(Base):
    __tablename__ = "regression_comparisons"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    run_a_id: Mapped[str] = mapped_column(ForeignKey("eval_runs.id"), nullable=False)
    run_b_id: Mapped[str] = mapped_column(ForeignKey("eval_runs.id"), nullable=False)
    metric_name: Mapped[str] = mapped_column(String, nullable=False)
    value_a: Mapped[float] = mapped_column(nullable=False)
    value_b: Mapped[float] = mapped_column(nullable=False)
    delta: Mapped[float] = mapped_column(nullable=False)
    threshold: Mapped[float] = mapped_column(nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
