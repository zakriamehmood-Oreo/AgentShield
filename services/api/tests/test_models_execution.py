from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from agentshield_shared.db.base import Base
from agentshield_shared.db.models_business import Customer
from agentshield.db.models_execution import Citation, Conversation, Message, Span, ToolCall


def _sqlite_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_conversation_message_span_tool_call_citation_round_trip():
    session = _sqlite_session()
    customer = Customer(customer_key="CUST-0001", email_hash="hash-abc")
    session.add(customer)
    session.commit()

    conversation = Conversation(customer_id=customer.id, channel="chat", status="open")
    session.add(conversation)
    session.commit()

    message = Message(conversation_id=conversation.id, role="customer", content="Where is my order?")
    session.add(message)
    session.commit()

    span = Span(
        conversation_id=conversation.id,
        span_id="span-1",
        parent_span_id=None,
        name="retrieval",
        kind="retrieval",
        attributes={"query": "where is my order"},
        status="ok",
    )
    session.add(span)
    session.commit()

    tool_call = ToolCall(
        conversation_id=conversation.id,
        span_id=span.id,
        tool_name="track_shipment",
        arguments={"order_id": "o1"},
        caller_identity=customer.id,
        result={"status": "in_transit"},
        decision="ALLOW",
        policy_id=None,
        reasoning="Read-only lookup, no policy restriction applies.",
        monetary_impact=0,
        contains_untrusted_content=False,
    )
    session.add(tool_call)
    session.commit()

    citation = Citation(message_id=message.id, policy_id=None, passage="Shipping takes 3-5 days.", score=0.87)
    session.add(citation)
    session.commit()

    fetched_conversation = session.query(Conversation).one()
    assert fetched_conversation.customer_id == customer.id
    assert session.query(Message).one().content == "Where is my order?"
    assert session.query(Span).one().attributes["query"] == "where is my order"
    assert session.query(ToolCall).one().decision == "ALLOW"
    assert session.query(Citation).one().score == 0.87
