from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from agentshield_shared.db.base import Base
from agentshield_shared.db.models_business import Customer, Order, Policy, Shipment


def _sqlite_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_customer_order_shipment_round_trip():
    session = _sqlite_session()
    customer = Customer(customer_key="CUST-0001", email_hash="hash-abc", tier="standard")
    session.add(customer)
    session.commit()

    order = Order(
        customer_id=customer.id,
        order_number="ORD-0001",
        status="placed",
        total_amount=42.50,
        currency="USD",
        items=[{"sku": "WIDGET-1", "qty": 2}],
        notes="Please ship fast!",
    )
    session.add(order)
    session.commit()

    shipment = Shipment(
        order_id=order.id,
        carrier="synthetic-post",
        tracking_number="TRACK-0001",
        status="in_transit",
        history=[{"event": "label_created"}],
    )
    session.add(shipment)
    session.commit()

    fetched_order = session.query(Order).filter_by(order_number="ORD-0001").one()
    assert fetched_order.customer_id == customer.id
    assert fetched_order.items[0]["sku"] == "WIDGET-1"
    assert fetched_order.shipments[0].tracking_number == "TRACK-0001"
    assert fetched_order.customer.customer_key == "CUST-0001"


def test_policy_defaults():
    session = _sqlite_session()
    policy = Policy(policy_key="refund-001", title="Refund Policy", body="Refunds require...", version=1)
    session.add(policy)
    session.commit()
    fetched = session.query(Policy).filter_by(policy_key="refund-001").one()
    assert fetched.version == 1
    assert fetched.tags == []
