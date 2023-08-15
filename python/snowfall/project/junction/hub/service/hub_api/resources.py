from __future__ import annotations

from collections.abc import Iterable
from typing import ClassVar

from starlette import requests

from snowfall.project.junction.go.service.orders.v1 import (
    models_pb2 as order_models_pb2,
)
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models
from snowfall.stdlib.v1 import money_pb2

_SELF_HREF = "self"
_RELATIONSHIPS_FIELD = "data"


class Price(models.BaseModel):
    currency: str
    amount: str

    @classmethod
    def from_proto(cls, price: money_pb2.Money) -> Price:
        money_price = money.from_protobuf(price)

        return cls(
            currency=money_price.currency.code,
            amount=str(money_price),
        )

    @classmethod
    def from_protos(cls, prices: Iterable[money_pb2.Money]) -> Price:
        money_price = money.total(
            [money.from_protobuf(price) for price in prices],
        )

        return cls(
            currency=money_price.currency.code,
            amount=str(money_price),
        )


class TripBookingResource(models.Resource):
    api_type: ClassVar[str] = "trip-bookings"

    @classmethod
    def from_proto(
        cls,
        booking: order_models_pb2.Booking,
        request: requests.Request,
    ) -> TripBookingResource:
        return cls(
            id=booking.id,
            type=TripBookingResource.api_type,
            attributes={
                "totalPrice": Price.from_proto(
                    booking.total_price,
                ),
                "operatorBookingReferences": list(
                    booking.trip_result.operator_booking_references,
                ),
                "externalReference": booking.trip_result.record_locator,
            },
            relationships={
                "order": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=booking.order_id,
                        type="orders",
                    ),
                },
                "status": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=protobuf.enum_value_to_slug(
                            order_models_pb2.Booking.Status.DESCRIPTOR,
                            booking.status,
                        ),
                        type="booking-statuses",
                    ),
                },
                "details": {
                    _RELATIONSHIPS_FIELD: [
                        models.ResourceIdentifier(
                            id=details.id,
                            type="trip-booking-details",
                        )
                        for details in booking.trip_option.details
                    ],
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewBooking",
                        bookingId=booking.id,
                    ),
                ),
            },
        )
