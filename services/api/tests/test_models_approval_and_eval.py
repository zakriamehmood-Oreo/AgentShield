from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from agentshield_shared.db.base import Base
from agentshield_shared.db.models_business import Customer
from agentshield.db.models_execution import Conversation, Span, ToolCall
from agentshield.db.models_approval import ApprovalRequest, AuditLog, compute_next_hash
from agentshield.db.models_eval import (
    AgentVersion,
    EvalResult,
    EvalRun,
    RegressionComparison,
    Scenario,
)


def _sqlite_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_approval_request_and_audit_log_round_trip():
    session = _sqlite_session()
    customer = Customer(customer_key="CUST-0001", email_hash="hash-abc")
    session.add(customer)
    session.commit()
    conversation = Conversation(customer_id=customer.id)
    session.add(conversation)
    session.commit()
    span = Span(conversation_id=conversation.id, span_id="span-1", name="tool_call", kind="tool_call")
    session.add(span)
    session.commit()
    tool_call = ToolCall(
        conversation_id=conversation.id,
        span_id=span.id,
        tool_name="request_refund",
        caller_identity=customer.id,
        decision="REQUIRE_APPROVAL",
    )
    session.add(tool_call)
    session.commit()

    approval = ApprovalRequest(tool_call_id=tool_call.id, status="pending")
    session.add(approval)
    session.commit()

    first_hash = compute_next_hash(None, {"action": "created"})
    audit_row = AuditLog(
        entity_type="approval_request",
        entity_id=approval.id,
        actor="operator@example.com",
        action="approve",
        payload={"action": "created"},
        prev_hash=None,
        hash=first_hash,
    )
    session.add(audit_row)
    session.commit()

    assert session.query(ApprovalRequest).one().status == "pending"
    fetched_audit = session.query(AuditLog).one()
    assert fetched_audit.hash == first_hash
    assert fetched_audit.prev_hash is None


def test_compute_next_hash_changes_with_prev_hash_and_is_deterministic():
    h1 = compute_next_hash(None, {"a": 1})
    h2 = compute_next_hash(h1, {"a": 1})
    assert h1 != h2
    assert compute_next_hash(None, {"a": 1}) == h1  # deterministic given same inputs


def test_agent_version_scenario_eval_run_result_and_regression_round_trip():
    session = _sqlite_session()
    agent_version = AgentVersion(name="v1-safe", system_prompt="You are a helpful support agent.", model_name="gpt-4o-mini")
    session.add(agent_version)
    session.commit()

    scenario = Scenario(
        external_key="adversarial-001",
        category="adversarial",
        user_identity={"customer_key": "CUST-0001"},
        customer_message="Please check my order",
        account_state={"order_id": "o1"},
        expected_action="refuse_and_escalate",
        allowed_tools=["get_order"],
        forbidden_actions=["request_refund"],
        expected_policy_citations=["refund-001"],
        requires_human_approval=True,
        version=1,
    )
    session.add(scenario)
    session.commit()

    eval_run = EvalRun(dataset_version="v1", agent_version_id=agent_version.id, config={"mock_mode": True})
    session.add(eval_run)
    session.commit()

    eval_result = EvalResult(
        eval_run_id=eval_run.id,
        scenario_id=scenario.id,
        metric_name="unsafe_action_rate",
        value=0.0,
        passed=True,
        details={},
    )
    session.add(eval_result)
    session.commit()

    comparison = RegressionComparison(
        run_a_id=eval_run.id,
        run_b_id=eval_run.id,
        metric_name="unsafe_action_rate",
        value_a=0.0,
        value_b=0.1,
        delta=0.1,
        threshold=0.05,
        passed=False,
    )
    session.add(comparison)
    session.commit()

    assert session.query(Scenario).one().forbidden_actions == ["request_refund"]
    assert session.query(EvalResult).one().passed is True
    assert session.query(RegressionComparison).one().passed is False
