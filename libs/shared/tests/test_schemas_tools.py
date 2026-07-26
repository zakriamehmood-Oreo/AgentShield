import pytest
from pydantic import ValidationError

from agentshield_shared.schemas.tools import (
    EscalateToHumanRequest,
    GetCustomerRequest,
    GetOrderRequest,
    IssueDiscountRequest,
    RequestRefundRequest,
    TrackShipmentRequest,
    UpdateShippingAddressRequest,
)


def test_request_refund_request_valid():
    req = RequestRefundRequest(customer_id="c1", order_id="o1", amount=10.0, reason="damaged item")
    assert req.amount == 10.0


def test_request_refund_rejects_non_positive_amount():
    with pytest.raises(ValidationError):
        RequestRefundRequest(customer_id="c1", order_id="o1", amount=0, reason="x")


def test_issue_discount_rejects_over_100_percent():
    with pytest.raises(ValidationError):
        IssueDiscountRequest(customer_id="c1", order_id="o1", percent=150, reason="x")


def test_issue_discount_rejects_non_positive_percent():
    with pytest.raises(ValidationError):
        IssueDiscountRequest(customer_id="c1", order_id="o1", percent=0, reason="x")


def test_update_shipping_address_rejects_too_short_address():
    with pytest.raises(ValidationError):
        UpdateShippingAddressRequest(customer_id="c1", order_id="o1", new_address="a")


def test_get_customer_request_requires_customer_id():
    with pytest.raises(ValidationError):
        GetCustomerRequest()


def test_get_order_request_requires_customer_and_order_id():
    req = GetOrderRequest(customer_id="c1", order_id="o1")
    assert req.customer_id == "c1"


def test_track_shipment_request_shape():
    req = TrackShipmentRequest(customer_id="c1", order_id="o1")
    assert req.order_id == "o1"


def test_escalate_to_human_request_shape():
    req = EscalateToHumanRequest(customer_id="c1", conversation_id="conv1", reason="angry customer")
    assert req.reason == "angry customer"
