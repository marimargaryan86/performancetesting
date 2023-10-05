from __future__ import annotations

import datetime
import zoneinfo
from collections import defaultdict
from collections.abc import Iterable, Sequence
from typing import Any, ClassVar, Literal

import pydantic
from starlette import datastructures, requests

from snowfall.project.junction.go.service.offers.v1 import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.go.service.orders.v1 import (
    models_pb2 as order_models_pb2,
)
from snowfall.project.junction.go.service.places.v1 import (
    models_pb2 as place_models_pb2,
)
from snowfall.project.junction.go.service.places.v1 import places_pb2
from snowfall.project.junction.go.service.trips.v1alpha import trips_pb2
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models
from snowfall.stdlib.v1 import amqp_pb2, money_pb2

_SELF_HREF: Literal["self"] = "self"
_RELATIONSHIPS_FIELD: Literal["data"] = "data"


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


class OfferResource(models.Resource):
    api_type: ClassVar[str] = "offers"

    @classmethod
    def from_proto(
        cls,
        offer: offer_models_pb2.OfferAggregate,
        request: requests.Request,
    ) -> OfferResource:
        return cls(
            id=offer.id,
            type=OfferResource.api_type,
            attributes={
                "createdAt": protobuf.protobuf_to_datetime(offer.created_at),
                "expiresAt": protobuf.protobuf_to_datetime(offer.expires_at),
            },
            relationships={
                "groups": {
                    "data": [
                        models.ResourceIdentifier(
                            id=offer_group.id,
                            type=OfferGroupResource.api_type,
                        )
                        for offer_group in offer.groups
                    ],
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewOffer",
                        offerId=offer.id,
                    ),
                ),
            },
        )


class OfferGroupResource(models.Resource):
    api_type: ClassVar[str] = "offer-groups"

    @classmethod
    def from_proto(
        cls,
        group: offer_models_pb2.OfferGroup,
        request: requests.Request,
    ) -> OfferGroupResource:
        return cls(
            id=group.id,
            type=OfferGroupResource.api_type,
            meta={
                "providerId": group.provider_id,
            },
            attributes={
                "expiresAt": protobuf.protobuf_to_datetime(group.expires_at),
            },
            relationships={
                "options": {
                    "data": [
                        models.ResourceIdentifier(
                            id=offer.id,
                            type=OfferOptionResource.api_type,
                        )
                        for offer in group.offers
                    ],
                },
                "details": {
                    "data": [
                        models.ResourceIdentifier(
                            id=detail.id,
                            type=TripOfferGroupDetailsResource.api_type,
                        )
                        for detail in group.segments
                    ],
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewOfferGroup",
                        offerGroupId=group.id,
                    ),
                ),
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


class RouteIdentifiers(models.BaseModel):
    vendor: str
    operator: str | None = None


class TripOfferGroupDetailsResource(models.Resource):
    api_type: ClassVar[str] = "trip-offer-group-details"

    @classmethod
    def from_proto(
        cls,
        segment: offer_models_pb2.OfferSegment,
        request: requests.Request,
    ) -> TripOfferGroupDetailsResource:
        return cls(
            id=segment.id,
            type=TripOfferGroupDetailsResource.api_type,
            attributes={
                "legs": [OfferSegmentLeg.from_proto(leg) for leg in segment.legs],
                "vendor": segment.vendor,
                "operator": segment.operator or None,
                "routeIdentifiers": RouteIdentifiers(
                    vendor=segment.vehicle.number,
                    operator=None,
                ),
                "sequences": {
                    "trip": segment.trip_sequence,
                    "segment": segment.segment_sequence,
                },
            },
            relationships={
                "legType": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=protobuf.enum_value_to_slug(
                            enum_descriptor=models_pb2.Schedule.Type.DESCRIPTOR,
                            enum_value=segment.type,
                        ),
                        type=LegTypeResource.api_type,
                    ),
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewOfferGroupDetails",
                        offerGroupDetailsId=segment.id,
                    ),
                ),
            },
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


class PenaltyApplicableTo(models.BaseModel):
    date_of_birth_after: datetime.date | None = pydantic.Field(
        alias="dateOfBirthAfter",
    )
    date_of_birth_before: datetime.date | None = pydantic.Field(
        alias="dateOfBirthBefore",
    )

    @classmethod
    def from_proto(
        cls,
        applicable_to: offer_models_pb2.ApplicableTo,
    ) -> PenaltyApplicableTo:
        return cls(
            dateOfBirthAfter=(
                protobuf.protobuf_to_date(
                    applicable_to.date_of_birth_after,
                )
                if applicable_to.date_of_birth_after.ByteSize()
                else None
            ),
            dateOfBirthBefore=(
                protobuf.protobuf_to_date(
                    applicable_to.date_of_birth_before,
                )
                if applicable_to.date_of_birth_before.ByteSize()
                else None
            ),
        )


class Penalty(models.BaseModel):
    applicable_to: PenaltyApplicableTo = pydantic.Field(alias="applicableTo")
    penalty_type: str = pydantic.Field(alias="penaltyType")
    changeable: bool
    refundable: bool | None
    conditions_apply: bool | None = pydantic.Field(alias="conditionsApply")
    applicability: str
    price: Price | None

    @classmethod
    def from_proto(cls, penalty: offer_models_pb2.Penalty) -> Penalty:
        return cls(
            applicableTo=PenaltyApplicableTo.from_proto(penalty.applicable_to),
            penaltyType=protobuf.enum_value_to_slug(
                enum_descriptor=offer_models_pb2.Penalty.Type.DESCRIPTOR,
                enum_value=penalty.penalty_type,
            ),
            changeable=penalty.changeable,
            refundable=penalty.refundable,
            conditionsApply=penalty.conditions_apply,
            applicability=protobuf.enum_value_to_slug(
                enum_descriptor=offer_models_pb2.Penalty.Applicability.DESCRIPTOR,
                enum_value=penalty.applicability,
            ),
            price=Price.from_proto(penalty.price) if penalty.price.ByteSize() else None,
        )


class OfferOptionResource(models.Resource):
    api_type: ClassVar[str] = "offer-options"

    @classmethod
    def from_proto(
        cls,
        option: offer_models_pb2.Offer,
        request: requests.Request,
    ) -> OfferOptionResource:
        return cls(
            id=option.id,
            type=OfferOptionResource.api_type,
            attributes={
                "price": Price.from_proto(option.price),
                "priceBreakdown": [
                    PriceBreakdown.from_proto(price_breakdown)
                    for price_breakdown in option.price_breakdown
                ],
                "brandName": option.brand_name,
                "baggageAllowances": [
                    BaggageAllowance.from_proto(baggage)
                    for baggage in option.baggage_allowances
                ],
            },
            relationships={
                "details": {
                    "data": [
                        models.ResourceIdentifier(
                            id=detail.id,
                            type=TripOfferOptionDetailsResource.api_type,
                        )
                        for detail in option.segment_details
                    ],
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewOfferOption",
                        offerOptionId=option.id,
                    ),
                ),
            },
        )


class FareRule(models.BaseModel):
    title: str
    body: str

    @classmethod
    def from_proto(cls, rule: offer_models_pb2.FareRule) -> FareRule:
        return cls(
            title=rule.title,
            body=rule.body,
        )


class BaggageAllowance(models.BaseModel):
    is_included: bool = pydantic.Field(alias="isIncluded")
    applicable_to: PenaltyApplicableTo = pydantic.Field(alias="applicableTo")

    @classmethod
    def from_proto(cls, baggage: offer_models_pb2.BaggageAllowance) -> BaggageAllowance:
        return cls(
            isIncluded=baggage.free,
            applicableTo=PenaltyApplicableTo.from_proto(baggage.applicable_to),
        )


class OfferSegmentAmenity(models.BaseModel):
    availability: str

    @classmethod
    def from_proto(
        cls,
        amenity: offer_models_pb2.SegmentAmenity,
    ) -> OfferSegmentAmenity:
        return cls(
            availability=protobuf.enum_value_to_slug(
                enum_descriptor=offer_models_pb2.SegmentAmenity.Type.DESCRIPTOR,
                enum_value=amenity.availability,
            ),
        )


class OfferSegmentAmenities(models.BaseModel):
    beverage: OfferSegmentAmenity
    entertainment: OfferSegmentAmenity
    food: OfferSegmentAmenity
    power: OfferSegmentAmenity
    wifi: OfferSegmentAmenity

    @classmethod
    def from_proto(
        cls,
        amenities: offer_models_pb2.SegmentAmenities,
    ) -> OfferSegmentAmenities:
        return cls(
            beverage=OfferSegmentAmenity.from_proto(amenities.beverage),
            entertainment=OfferSegmentAmenity.from_proto(amenities.entertainment),
            food=OfferSegmentAmenity.from_proto(amenities.food),
            power=OfferSegmentAmenity.from_proto(amenities.power),
            wifi=OfferSegmentAmenity.from_proto(amenities.wifi),
        )


class TripOfferOptionDetailsResource(models.Resource):
    api_type: ClassVar[str] = "trip-offer-option-details"

    @classmethod
    def from_proto(
        cls,
        details: offer_models_pb2.OfferSegmentDetails,
        request: requests.Request,
    ) -> TripOfferOptionDetailsResource:
        return cls(
            id=details.id,
            type=TripOfferOptionDetailsResource.api_type,
            attributes={
                "cabinClassName": details.cabin_class.marketing_name,
                "baggageAllowances": [
                    BaggageAllowance.from_proto(baggage)
                    for baggage in details.baggage_allowances
                ],
                "amenities": OfferSegmentAmenities.from_proto(details.amenities),
            },
            relationships={
                "details": {
                    "data": models.ResourceIdentifier(
                        id=details.offer_segment_id,
                        type=TripOfferGroupDetailsResource.api_type,
                    ),
                },
                "cabinClass": {
                    "data": models.ResourceIdentifier(
                        id=protobuf.enum_value_to_slug(
                            enum_descriptor=models_pb2.CabinClass.Type.DESCRIPTOR,
                            enum_value=details.cabin_class.type,
                        ),
                        type=CabinClassResource.api_type,
                    ),
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewOfferOptionDetails",
                        offerOptionDetailsId=details.id,
                    ),
                ),
            },
        )


class CabinClass(models.BaseModel):
    name: str
    marketing_name: str = pydantic.Field(alias="marketingName")

    @classmethod
    def from_proto(cls, cabin_class: models_pb2.CabinClass) -> CabinClass:
        return cls(
            name=protobuf.enum_value_to_slug(
                enum_descriptor=models_pb2.CabinClass.Type.DESCRIPTOR,
                enum_value=cabin_class.type,
            ),
            marketingName=cabin_class.marketing_name,
        )


class OfferSegmentDetails(models.BaseModel):
    ref: str
    cabin_class: CabinClass = pydantic.Field(alias="cabinClass")

    @classmethod
    def from_proto(
        cls,
        details: offer_models_pb2.OfferSegmentDetails,
    ) -> OfferSegmentDetails:
        return cls(
            ref=details.id,
            cabinClass=CabinClass.from_proto(details.cabin_class),
        )


class PriceBreakdown(models.BaseModel):
    price: Price
    breakdown_type: str = pydantic.Field(alias="breakdownType")

    @classmethod
    def from_proto(
        cls,
        price_breakdown: offer_models_pb2.PriceBreakdown,
    ) -> PriceBreakdown:
        return cls(
            price=Price.from_proto(price_breakdown.price),
            breakdownType=protobuf.enum_value_to_slug(
                enum_descriptor=offer_models_pb2.PriceBreakdown.BreakdownType.DESCRIPTOR,
                enum_value=price_breakdown.breakdown_type,
            ),
        )

    @classmethod
    def from_protos(
        cls,
        price_breakdown_protos: Iterable[offer_models_pb2.PriceBreakdown],
    ) -> list[PriceBreakdown]:
        price_breakdowns_by_type = defaultdict[
            offer_models_pb2.PriceBreakdown.BreakdownType.ValueType,
            list[offer_models_pb2.PriceBreakdown],
        ](list)
        for price_breakdown in price_breakdown_protos:
            price_breakdowns_by_type[price_breakdown.breakdown_type].append(
                price_breakdown,
            )

        return [
            cls(
                price=Price.from_protos(
                    [breakdown.price for breakdown in price_breakdowns],
                ),
                breakdownType=protobuf.enum_value_to_slug(
                    enum_descriptor=offer_models_pb2.PriceBreakdown.BreakdownType.DESCRIPTOR,
                    enum_value=breakdown_type,
                ),
            )
            for breakdown_type, price_breakdowns in price_breakdowns_by_type.items()
        ]


class PriceQuoteResource(models.Resource):
    api_type: ClassVar[str] = "trip-offer-price-quotes"

    @classmethod
    def from_proto(
        cls,
        price_quote: offer_models_pb2.PriceQuoteContainer,
        request: requests.Request,
    ) -> PriceQuoteResource:
        if len(price_quote.quotes) < len(price_quote.option_ids):
            status = "pending"
            price = None
        else:
            status = "completed"
            price = Price.from_protos(
                [quote.price for quote in price_quote.quotes],
            )

        return cls(
            id=price_quote.id,
            type=PriceQuoteResource.api_type,
            attributes={
                "expiresAt": protobuf.protobuf_to_datetime(price_quote.expires_at),
                "price": price,
                "priceBreakdown": PriceBreakdown.from_protos(
                    [
                        price_breakdown
                        for quote in price_quote.quotes
                        for price_breakdown in quote.price_breakdown
                    ],
                ),
                "penalties": [
                    Penalty.from_proto(penalty)
                    for quote in price_quote.quotes
                    for penalty in quote.penalties
                ],
                "required": [
                    protobuf.enum_value_to_slug(
                        enum_descriptor=offer_models_pb2.PriceQuote.Required.DESCRIPTOR,
                        enum_value=required_value,
                    )
                    for quote in price_quote.quotes
                    for required_value in quote.required_documents
                ],
                "rules": [
                    FareRule.from_proto(rule)
                    for quote in price_quote.quotes
                    for rule in quote.rules
                ],
                "status": status,
            },
            relationships={
                "offer": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=price_quote.offer_id,
                        type=OfferResource.api_type,
                    ),
                },
                "options": {
                    _RELATIONSHIPS_FIELD: [
                        models.ResourceIdentifier(
                            id=option_id,
                            type=OfferOptionResource.api_type,
                        )
                        for option_id in price_quote.option_ids
                    ],
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewPriceQuote",
                        offerPriceQuoteId=price_quote.id,
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
                            type=OrderResource.api_type,
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


class BookingStatusResource(models.Resource):
    api_type: ClassVar[str] = "booking-statuses"


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
                "totalPrice": Price.from_proto(booking.total_price),
                "operatorBookingReferences": list(
                    booking.trip_result.operator_booking_references,
                ),
                "externalReference": booking.trip_result.record_locator,
                "ticketUrls": list(booking.ticket_urls),
            },
            relationships={
                "order": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=booking.order_id,
                        type=OrderResource.api_type,
                    ),
                },
                "status": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=protobuf.enum_value_to_slug(
                            order_models_pb2.Booking.Status.DESCRIPTOR,
                            booking.status,
                        ),
                        type=BookingStatusResource.api_type,
                    ),
                },
                "details": {
                    _RELATIONSHIPS_FIELD: [
                        models.ResourceIdentifier(
                            id=details.id,
                            type=TripBookingDetailsResource.api_type,
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


class PlaceResource(models.Resource):
    api_type: ClassVar[str] = "places"

    @classmethod
    def from_proto(
        cls,
        place: place_models_pb2.Place,
        request: requests.Request,
    ) -> PlaceResource:
        return cls(
            id=place.location.id,
            type=PlaceResource.api_type,
            attributes={
                "countryCode": place.location.country_code or "GB",
                "iataCode": place.place_attributes.iata or None,
                "latitude": place.location.coordinates.latitude,
                "longitude": place.location.coordinates.longitude,
                "name": place.location.name,
                "timeZone": place.location.time_zone,
                "updatedAt": protobuf.protobuf_to_datetime(place.location.updated_at),
            },
            relationships={
                "types": {
                    _RELATIONSHIPS_FIELD: [
                        models.ResourceIdentifier(
                            id=protobuf.enum_value_to_slug(
                                enum_descriptor=place_models_pb2.Location.Type.DESCRIPTOR,
                                enum_value=place_type,
                            ),
                            type=PlaceTypeResource.api_type,
                        )
                        for place_type in place.location.types
                    ],
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewPlace",
                        placeId=place.location.id,
                    ),
                ),
            },
        )


class PlaceTypeResource(models.Resource):
    api_type: ClassVar[str] = "place-types"

    @classmethod
    def from_proto(
        cls,
        place_type: place_models_pb2.Location.Type.ValueType,
        self_link: datastructures.URL,
    ) -> PlaceTypeResource:
        place_type_id = protobuf.enum_value_to_slug(
            enum_descriptor=place_models_pb2.Location.Type.DESCRIPTOR,
            enum_value=place_type,
        )
        return cls(
            id=place_type_id,
            type=PlaceTypeResource.api_type,
            attributes={
                "name": place_type_id,
            },
            links={
                _SELF_HREF: str(self_link),
            },
        )


class PassengerGenderResource(models.Resource):
    api_type: ClassVar[str] = "passenger-genders"

    @classmethod
    def from_proto(
        cls,
        passenger_gender: order_models_pb2.Passenger.Gender.ValueType,
        self_link: datastructures.URL,
    ) -> PassengerGenderResource:
        passenger_gender_id = protobuf.enum_value_to_slug(
            enum_descriptor=order_models_pb2.Passenger.Gender.DESCRIPTOR,
            enum_value=passenger_gender,
        )
        return cls(
            id=passenger_gender_id,
            type=PassengerGenderResource.api_type,
            attributes={
                "name": passenger_gender_id,
            },
            links={
                _SELF_HREF: str(self_link),
            },
        )


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


class PassengerTitleResource(models.Resource):
    api_type: ClassVar[str] = "passenger-titles"

    @classmethod
    def from_proto(
        cls,
        passenger_title: order_models_pb2.Passenger.Title.ValueType,
        self_link: datastructures.URL,
    ) -> PassengerTitleResource:
        passenger_title_id = protobuf.enum_value_to_slug(
            enum_descriptor=order_models_pb2.Passenger.Title.DESCRIPTOR,
            enum_value=passenger_title,
        )
        return cls(
            id=passenger_title_id,
            type=PassengerTitleResource.api_type,
            attributes={
                "name": passenger_title_id,
            },
            links={
                _SELF_HREF: str(self_link),
            },
        )


class SegmentResource(models.Resource):
    api_type: ClassVar[str] = "segments"

    @classmethod
    def from_proto(
        cls,
        segment: models_pb2.SegmentReference,
        schedule: models_pb2.Schedule,
        request: requests.Request,
    ) -> SegmentResource:
        return cls(
            id=segment.id,
            type=SegmentResource.api_type,
            attributes={
                "name": schedule.name,
                "operator": schedule.agency_name,
            },
            relationships={
                "legs": {
                    _RELATIONSHIPS_FIELD: [
                        models.ResourceIdentifier(
                            id=leg_id,
                            type=LegResource.api_type,
                        )
                        for leg_id in segment.leg_ids
                    ],
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewSegment",
                        segmentId=segment.id,
                    ),
                ),
            },
        )


class LegResource(models.Resource):
    api_type: ClassVar[str] = "legs"

    @classmethod
    def from_proto(
        cls,
        leg: models_pb2.Leg,
        request: requests.Request,
    ) -> LegResource:
        return cls(
            id=leg.id,
            type=LegResource.api_type,
            attributes={
                "departureAt": protobuf.protobuf_to_datetime(
                    leg.departure_at,
                ).astimezone(zoneinfo.ZoneInfo(leg.origin.time_zone)),
                "arrivalAt": protobuf.protobuf_to_datetime(
                    leg.arrival_at,
                ).astimezone(zoneinfo.ZoneInfo(leg.destination.time_zone)),
                "origin": Point.from_proto(leg.origin),
                "destination": Point.from_proto(leg.destination),
            },
            relationships={
                "legType": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=protobuf.enum_value_to_slug(
                            enum_descriptor=models_pb2.Schedule.Type.DESCRIPTOR,
                            enum_value=leg.type,
                        ),
                        type=LegTypeResource.api_type,
                    ),
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewLeg",
                        legId=leg.id,
                    ),
                ),
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


class TripResource(models.Resource):
    api_type: ClassVar[str] = "trips"

    @classmethod
    def from_proto(
        cls,
        trip: models_pb2.TripReference,
        request: requests.Request,
    ) -> TripResource:
        return cls(
            id=trip.id,
            type=TripResource.api_type,
            attributes={},
            relationships={
                "segments": {
                    _RELATIONSHIPS_FIELD: [
                        models.ResourceIdentifier(
                            id=segment.id,
                            type=SegmentResource.api_type,
                        )
                        for segment in trip.segments
                    ],
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewTrip",
                        tripId=trip.id,
                    ),
                ),
            },
        )


class TripSearchResource(models.Resource):
    api_type: ClassVar[str] = "trip-searches"

    @classmethod
    def from_proto(
        cls,
        trip_search: trips_pb2.TripSearch,
        request: requests.Request,
    ) -> TripSearchResource:
        return cls(
            id=trip_search.id,
            type=TripSearchResource.api_type,
            attributes={
                "expiresAt": protobuf.protobuf_to_datetime(
                    trip_search.expires_at,
                ),
                "departureAfter": protobuf.protobuf_to_datetime(
                    trip_search.departure_after,
                ),
                "status": protobuf.enum_value_to_slug(
                    amqp_pb2.Trackable.Status.DESCRIPTOR,
                    trip_search.status,
                ),
            },
            relationships={
                "origin": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=trip_search.origins[0].ref,
                        type=PlaceResource.api_type,
                    ),
                },
                "destination": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=trip_search.destinations[0].ref,
                        type=PlaceResource.api_type,
                    ),
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewTripSearch",
                        tripSearchId=trip_search.id,
                    ),
                ),
            },
        )


class TripOfferSearchResource(models.Resource):
    api_type: ClassVar[str] = "trip-offer-searches"

    @classmethod
    def from_proto(
        cls,
        offer_search: offer_models_pb2.OfferSearch,
        offers: Sequence[offer_models_pb2.OfferAggregateMapping],
        request: requests.Request,
    ) -> TripOfferSearchResource:
        return cls(
            id=offer_search.id,
            type=TripOfferSearchResource.api_type,
            attributes=cls._get_attributes(offer_search),
            relationships={
                "offers": {
                    _RELATIONSHIPS_FIELD: [
                        models.ResourceIdentifier(
                            id=offer.id,
                            type=OfferResource.api_type,
                        )
                        for offer in offers
                    ],
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewOfferSearch",
                        offerSearchId=offer_search.id,
                    ),
                ),
            },
        )

    @classmethod
    def _get_attributes(
        cls,
        offer_search: offer_models_pb2.OfferSearch,
    ) -> dict[str, Any]:
        attributes = {
            "expiresAt": protobuf.protobuf_to_datetime(
                offer_search.expires_at,
            ),
            "passengers": [
                {"dateOfBirth": protobuf.protobuf_to_date(passenger.date_of_birth)}
                for passenger in offer_search.trip.passengers
            ],
            "status": protobuf.enum_value_to_slug(
                amqp_pb2.Trackable.Status.DESCRIPTOR,
                offer_search.status,
            ),
        }

        if offer_search.trip.HasField("loyalty_card"):
            attributes["loyalty"] = {
                "airlineIata": offer_search.trip.loyalty_card.airline_iata,
                "number": offer_search.trip.loyalty_card.number,
                "firstName": offer_search.trip.loyalty_card.first_name,
                "lastName": offer_search.trip.loyalty_card.last_name,
            }

        return attributes


class TripCandidateSearchResource(models.Resource):
    api_type: ClassVar[str] = "trip-candidate-searches"

    @classmethod
    def from_proto(
        cls,
        trip_candidate_search: trips_pb2.TripCandidateSearch,
        request: requests.Request,
    ) -> TripCandidateSearchResource:
        return cls(
            id=trip_candidate_search.id,
            type=cls.api_type,
            attributes={
                "passengers": [
                    {
                        "dateOfBirth": protobuf.protobuf_to_date(
                            passenger.date_of_birth,
                        ),
                    }
                    for passenger in trip_candidate_search.passengers
                ],
                "criteria": [
                    {
                        "origin": {
                            "latitude": criteria.origin.coordinates.latitude,
                            "longitude": criteria.origin.coordinates.longitude,
                            "precision": protobuf.enum_value_to_slug(
                                places_pb2.SearchPrecision.Mode.DESCRIPTOR,
                                criteria.origin.precision.mode,
                            ),
                        },
                        "destination": {
                            "latitude": criteria.destination.coordinates.latitude,
                            "longitude": criteria.destination.coordinates.longitude,
                            "precision": protobuf.enum_value_to_slug(
                                places_pb2.SearchPrecision.Mode.DESCRIPTOR,
                                criteria.destination.precision.mode,
                            ),
                        },
                        "departureAfter": protobuf.protobuf_to_datetime(
                            criteria.departure_after,
                        ),
                        "maximumConnections": criteria.maximum_connections,
                    }
                    for criteria in trip_candidate_search.criteria
                ],
                "expiresAt": protobuf.protobuf_to_datetime(
                    trip_candidate_search.expires_at,
                ),
                "status": protobuf.enum_value_to_slug(
                    amqp_pb2.Trackable.Status.DESCRIPTOR,
                    trip_candidate_search.status,
                ),
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewTripCandidateSearch",
                        tripCandidateSearchId=trip_candidate_search.id,
                    ),
                ),
            },
        )


class CancellationRequestResource(models.Resource):
    api_type: ClassVar[str] = "cancellation-request"

    @classmethod
    def from_proto(
        cls,
        cancellation_request: order_models_pb2.CancellationRequest,
        request: requests.Request,
    ) -> CancellationRequestResource:
        request_model = order_models_pb2.CancellationRequest
        status = protobuf.enum_value_to_slug(
            enum_descriptor=request_model.Status.DESCRIPTOR,
            enum_value=cancellation_request.status,
        )
        return cls(
            id=cancellation_request.id,
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
                        for booking_cancellation in cancellation_request.booking_cancellations
                    ],
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewCancellationRequest",
                        cancellationRequestId=cancellation_request.id,
                    ),
                ),
            },
        )


class BookingCancellationResource(models.Resource):
    api_type: ClassVar[str] = "booking-cancellation"

    @classmethod
    def from_proto(
        cls,
        booking_cancellation: order_models_pb2.BookingCancellation,
        request: requests.Request,
    ) -> BookingCancellationResource:
        request_model = order_models_pb2.BookingCancellation
        status = protobuf.enum_value_to_slug(
            enum_descriptor=request_model.Status.DESCRIPTOR,
            enum_value=booking_cancellation.status,
        )
        return cls(
            id=booking_cancellation.id,
            type=cls.api_type,
            attributes={
                "status": status,
            },
            relationships={
                "booking": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=booking_cancellation.booking_id,
                        type=TripBookingResource.api_type,
                    ),
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewBookingCancellationByBooking",
                        bookingId=booking_cancellation.booking_id,
                    ),
                ),
            },
        )
