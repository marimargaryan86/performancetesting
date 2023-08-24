from __future__ import annotations

import datetime
import zoneinfo
from collections.abc import Iterable
from typing import ClassVar

from pydantic import v1 as pydantic
from starlette import datastructures, requests

from snowfall.project.junction.go.service.offers.v1 import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.go.service.orders.v1 import (
    models_pb2 as order_models_pb2,
)
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models
from snowfall.stdlib.v1 import money_pb2

_SELF_HREF = "self"
_RELATIONSHIPS_FIELD = "data"


class Point(models.BaseModel):
    ref: str
    name: str
    latitude: float
    longitude: float
    time_zone: str = pydantic.Field(alias="timeZone")

    @classmethod
    def from_proto(cls, point: models_pb2.Point) -> Point:
        return cls(
            ref=point.ref,
            name=point.name,
            latitude=point.coordinates.latitude,
            longitude=point.coordinates.longitude,
            timeZone=point.time_zone,
        )


class RouteIdentifiers(models.BaseModel):
    vendor: str
    operator: str | None = None


class CabinClassResource(models.Resource):
    api_type: ClassVar[str] = "cabin-classes"

    @classmethod
    def from_proto(
        cls,
        cabin_class: models_pb2.CabinClass.Type.ValueType,
        self_link: datastructures.URL,
    ) -> CabinClassResource:
        cabin_class_id = protobuf.enum_value_to_slug(
            enum_descriptor=models_pb2.CabinClass.Type.DESCRIPTOR,
            enum_value=cabin_class,
        )
        return cls(
            id=cabin_class_id,
            type=CabinClassResource.api_type,
            attributes={
                "name": cabin_class_id,
            },
            links={
                _SELF_HREF: str(self_link),
            },
        )


class LegTypeResource(models.Resource):
    api_type: ClassVar[str] = "leg-types"

    @classmethod
    def from_proto(
        cls,
        schedule_type: models_pb2.Schedule.Type.ValueType,
        self_link: datastructures.URL,
    ) -> LegTypeResource:
        schedule_type_id = protobuf.enum_value_to_slug(
            enum_descriptor=models_pb2.Schedule.Type.DESCRIPTOR,
            enum_value=schedule_type,
        )
        return cls(
            id=schedule_type_id,
            type=LegTypeResource.api_type,
            attributes={
                "name": schedule_type_id,
            },
            links={
                _SELF_HREF: str(self_link),
            },
        )


class OfferSegmentLeg(models.BaseModel):
    origin: Point
    destination: Point
    departure_at: datetime.datetime = pydantic.Field(alias="departureAt")
    arrival_at: datetime.datetime = pydantic.Field(alias="arrivalAt")

    @classmethod
    def from_proto(cls, leg: offer_models_pb2.OfferSegmentLeg) -> OfferSegmentLeg:
        return cls(
            origin=Point.from_proto(leg.origin),
            destination=Point.from_proto(leg.destination),
            departureAt=protobuf.protobuf_to_datetime(leg.departure_at).astimezone(
                zoneinfo.ZoneInfo(leg.origin.time_zone),
            ),
            arrivalAt=protobuf.protobuf_to_datetime(leg.arrival_at).astimezone(
                zoneinfo.ZoneInfo(leg.destination.time_zone),
            ),
        )


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


class TripBookingDetailsResource(models.Resource):
    api_type: ClassVar[str] = "trip-booking-details"

    @classmethod
    def from_proto(
        cls,
        details: order_models_pb2.TripOptionDetails,
        request: requests.Request,
    ) -> TripBookingDetailsResource:
        return cls(
            id=details.id,
            type=TripBookingDetailsResource.api_type,
            attributes={
                "cabinClassName": details.cabin_class.marketing_name,
                "vendor": details.segment.vendor,
                "operator": details.segment.operator or None,
                "routeIdentifiers": RouteIdentifiers(
                    vendor=details.segment.vehicle.number,
                    operator=None,
                ),
                "legs": [
                    OfferSegmentLeg.from_proto(leg) for leg in details.segment.legs
                ],
            },
            relationships={
                "booking": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=details.booking_id,
                        type=TripBookingResource.api_type,
                    ),
                },
                "cabinClass": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=protobuf.enum_value_to_slug(
                            enum_descriptor=models_pb2.CabinClass.Type.DESCRIPTOR,
                            enum_value=details.cabin_class.type,
                        ),
                        type=CabinClassResource.api_type,
                    ),
                },
                "legType": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=protobuf.enum_value_to_slug(
                            enum_descriptor=models_pb2.Schedule.Type.DESCRIPTOR,
                            enum_value=details.segment.type,
                        ),
                        type=LegTypeResource.api_type,
                    ),
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewBookingDetails",
                        bookingDetailsId=details.id,
                    ),
                ),
            },
        )


class JourneyResource(models.Resource):
    api_type: ClassVar[str] = "journeys"

    @classmethod
    def from_proto(
        cls,
        journey: order_models_pb2.Journey,
        request: requests.Request,
    ) -> JourneyResource:
        return cls(
            id=journey.id,
            type=JourneyResource.api_type,
            attributes={
                "reference": journey.passenger_name_record,
                "contactDetails": {
                    "email": journey.contact_details.email,
                    "address": {
                        "addressLines": list(
                            journey.contact_details.address.address_lines,
                        ),
                        "countryCode": journey.contact_details.address.region_code,
                        "postalCode": journey.contact_details.address.postal_code,
                        "city": journey.contact_details.address.locality,
                    },
                    "phoneNumber": journey.contact_details.phone.e164_number,
                },
            },
            relationships={
                "orders": {
                    _RELATIONSHIPS_FIELD: [
                        models.ResourceIdentifier(
                            id=order.id,
                            type="orders",
                        )
                        for order in journey.orders
                    ],
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewJourney",
                        journeyId=journey.id,
                    ),
                ),
            },
        )


class OrderResource(models.Resource):
    api_type: ClassVar[str] = "orders"

    @classmethod
    def from_proto(
        cls,
        order: order_models_pb2.Order,
        request: requests.Request,
    ) -> OrderResource:
        return cls(
            id=order.id,
            type=OrderResource.api_type,
            attributes={
                "passengers": [
                    {
                        "firstName": passenger.first_name,
                        "dateOfBirth": protobuf.protobuf_to_date(
                            passenger.date_of_birth,
                        ),
                        "title": protobuf.enum_value_to_slug(
                            enum_descriptor=order_models_pb2.Passenger.Title.DESCRIPTOR,
                            enum_value=passenger.title,
                        ),
                        "lastName": passenger.last_name,
                        "gender": protobuf.enum_value_to_slug(
                            enum_descriptor=order_models_pb2.Passenger.Gender.DESCRIPTOR,
                            enum_value=passenger.gender,
                        ),
                    }
                    for passenger in order.passengers
                ],
            },
            relationships={
                "journey": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=order.journey_id,
                        type=JourneyResource.api_type,
                    ),
                },
                "bookings": {
                    _RELATIONSHIPS_FIELD: [
                        models.ResourceIdentifier(
                            id=booking.id,
                            type=TripBookingResource.api_type,
                        )
                        for booking in order.bookings
                    ],
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewOrder",
                        orderId=order.id,
                    ),
                ),
            },
        )


class BookingsCancellationResource(models.Resource):
    api_type: ClassVar[str] = "bookings-cancellations"

    @classmethod
    def from_proto(
        cls,
        cancellation: order_models_pb2.BookingsCancellation,
        request: requests.Request,
    ) -> BookingsCancellationResource:
        request_model = order_models_pb2.BookingsCancellation
        status = protobuf.enum_value_to_slug(
            enum_descriptor=request_model.Status.DESCRIPTOR,
            enum_value=cancellation.status,
        )
        return cls(
            id=cancellation.id,
            type=cls.api_type,
            attributes={
                "status": status,
            },
            relationships={
                "bookings": {
                    _RELATIONSHIPS_FIELD: [
                        models.ResourceIdentifier(
                            id=booking_cancellation.booking_id,
                            type=TripBookingResource.api_type,
                        )
                        for booking_cancellation in cancellation.booking_cancellations
                    ],
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewBookingsCancellation",
                        bookingsCancellationId=cancellation.id,
                    ),
                ),
            },
        )
