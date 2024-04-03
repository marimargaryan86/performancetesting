from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any

import pydantic

from snowfall.vendor.duffel.builders.base import DuffelRequestBaseModel


class OrderService(DuffelRequestBaseModel):
    quantity: int
    service_id: str = pydantic.Field(alias="id")


class OrderPayment(DuffelRequestBaseModel):
    payment_type: str = pydantic.Field(alias="type")
    currency: str
    amount: str


class IdentityDocument(DuffelRequestBaseModel):
    unique_identifier: str
    document_type: str = pydantic.Field(alias="type")
    issuing_country_code: str
    expires_on: datetime.date


class OrderPassenger(DuffelRequestBaseModel):
    title: str
    phone_number: str
    infant_passenger_id: str | None = None
    identity_documents: list[IdentityDocument] | None = None
    passenger_id: str = pydantic.Field(alias="id")
    given_name: str
    gender: str
    family_name: str
    email: str
    born_on: datetime.date


class Metadata(DuffelRequestBaseModel):
    payment_intent_id: str


class OrderDataElements(DuffelRequestBaseModel):
    order_type: str | None = pydantic.Field(alias="type")
    services: list[OrderService] | None = None
    selected_offers: list[str]
    payments: list[OrderPayment]
    passengers: list[OrderPassenger]
    metadata: Mapping[str, Any] | None = None


class OrderData(DuffelRequestBaseModel):
    order_data: OrderDataElements = pydantic.Field(alias="data")


class OrderBuilder:
    def __init__(self) -> None:
        self._passengers: list[OrderPassenger] = []
        self._payments: list[OrderPayment] = []
        self._selected_offers: list[str] = []
        self._services: list[OrderService] = []
        self._type_order: str | None = None
        self._metadata_object: Mapping[str, Any] | None = None

    def order_type(self, order_t: str) -> OrderBuilder:
        self._type_order = order_t
        return self

    def add_passenger(self, passenger: OrderPassenger) -> OrderBuilder:
        self._passengers.append(passenger)
        return self

    def add_payment(self, payment: OrderPayment) -> OrderBuilder:
        self._payments.append(payment)
        return self

    def add_service(self, service: OrderService) -> OrderBuilder:
        self._services.append(service)
        return self

    def add_offer_id(self, offer_id: str) -> OrderBuilder:
        self._selected_offers.append(offer_id)
        return self

    def metadata(self, metadata: Mapping[str, Any]) -> OrderBuilder:
        self._metadata_object = metadata
        return self

    def build(self) -> OrderData:
        return OrderData(
            order_data=OrderDataElements(
                order_type=self._type_order,
                services=self._services,
                payments=self._payments,
                passengers=self._passengers,
                selected_offers=self._selected_offers,
                metadata=self._metadata_object,
            ),
        )
