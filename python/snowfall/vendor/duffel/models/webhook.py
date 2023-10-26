import datetime
from enum import StrEnum
from typing import Any

from pydantic import Field

from snowfall.vendor.duffel.models.base import (
    DuffelBaseModel,
    DuffelListRequest,
    RemoteListPage,
)


class WebhookEventType(StrEnum):
    order_airline_initiated_change = "order.airline_initiated_change_detected"
    order_created = "order.created"


class Webhook(DuffelBaseModel):
    identifier: str = Field(alias="id")
    url: str
    updated_at: str
    created_at: str
    live_mode: bool
    events: set[WebhookEventType]
    active: bool


class WebhookCreateRequest(DuffelBaseModel):
    url: str
    events: list[str]


class WebhookDelivery(DuffelBaseModel):
    identifier: str = Field(alias="id")
    event_type: str = Field(alias="type")
    url: str
    response_status_code: int
    response_body: str
    live_mode: bool
    event_id: str
    endpoint_id: str
    created_at: datetime.datetime


class WebhookDeliveryListRequest(DuffelListRequest):
    event_type: WebhookEventType = Field(alias="type")
    created_at: datetime.datetime | None
    delivery_success: bool | None
    endpoint_id: str | None


class WebhookCreateResponse(Webhook):
    secret: str


class WebhookEvent(DuffelBaseModel):
    identifier: str = Field(alias="id")
    event_type: WebhookEventType = Field(alias="type")
    api_version: str
    created_at: datetime.datetime
    data: dict[str, Any]
    idempotency_key: str
    identity_organisation_id: str
    live_mode: bool

    def identity(self) -> str:
        return self.identifier


class WebhookPingResponse(DuffelBaseModel):
    identifier: str = Field(alias="id")


class WebhookListPage(RemoteListPage[Webhook]):
    data: list[Webhook]
