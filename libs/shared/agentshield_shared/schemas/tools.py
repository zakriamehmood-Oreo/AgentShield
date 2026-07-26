"""Typed request/response schemas for the 7 mock business tools.

Used by services/tool_server to implement the tools AND independently by
the gateway (services/api) to validate arguments and results before/after
forwarding — the two services never trust each other's validation alone.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class GetCustomerRequest(BaseModel):
    customer_id: str


class GetCustomerResponse(BaseModel):
    customer_id: str
    customer_key: str
    tier: str
    email_hash: str


class GetOrderRequest(BaseModel):
    customer_id: str
    order_id: str


class GetOrderResponse(BaseModel):
    order_id: str
    order_number: str
    status: str
    total_amount: float
    currency: str
    items: list[dict]
    notes: str


class TrackShipmentRequest(BaseModel):
    customer_id: str
    order_id: str


class TrackShipmentResponse(BaseModel):
    shipment_id: str
    carrier: str
    tracking_number: str
    status: str
    eta: datetime | None
    history: list[dict]


class UpdateShippingAddressRequest(BaseModel):
    customer_id: str
    order_id: str
    new_address: str = Field(min_length=5, max_length=500)


class UpdateShippingAddressResponse(BaseModel):
    order_id: str
    updated: bool
    new_address: str


class RequestRefundRequest(BaseModel):
    customer_id: str
    order_id: str
    amount: float = Field(gt=0)
    reason: str


class RequestRefundResponse(BaseModel):
    order_id: str
    refund_id: str
    amount: float
    status: str  # "issued" | "pending_approval"


class IssueDiscountRequest(BaseModel):
    customer_id: str
    order_id: str
    percent: float = Field(gt=0, le=100)
    reason: str


class IssueDiscountResponse(BaseModel):
    order_id: str
    discount_id: str
    percent: float
    status: str


class EscalateToHumanRequest(BaseModel):
    customer_id: str
    conversation_id: str
    reason: str


class EscalateToHumanResponse(BaseModel):
    escalation_id: str
    status: str
