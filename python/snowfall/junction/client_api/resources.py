from __future__ import annotations

import datetime
import zoneinfo
from typing import Any, Optional, Sequence

import pydantic
from starlette import requests

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.offers.v1alpha import models_pb2 as offer_models_pb2
from snowfall.junction.orders.v1alpha import models_pb2 as order_models_pb2
from snowfall.junction.trips.v1alpha import trips_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models

_SELF_HREF = "self"
_RELATIONSHIPS_FIELD = "data"
_OFFERS_TYPE = "offer-aggregates"


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
    @classmethod
    def from_proto(
        cls,
        offer: offer_models_pb2.OfferAggregate,
        request: requests.Request,
    ) -> OfferResource:
        return cls(
            id=offer.id,
            type=_OFFERS_TYPE,
            attributes=cls._get_attributes(offer),
            links={
                _SELF_HREF: request.url_for(
                    "ViewOffer",
                    offerId=offer.id,
                ),
            },
        )

    @classmethod
    def _get_attributes(
        cls,
        offer: offer_models_pb2.OfferAggregate,
    ) -> dict[str, Any]:
        return {
            "groups": [
                OfferGroup.from_proto(offer_group) for offer_group in offer.groups
            ],
            "expiresAt": protobuf.protobuf_to_datetime(offer.expires_at),
        }


class Price(models.BaseModel):
    currency: str
    amount: str

    @classmethod
    def from_proto(cls, price: models_pb2.Price) -> Price:
        return cls(
            currency=price.currency,
            amount=str(price.amount / 100),
        )


class CabinClass(models.BaseModel):
    name: str
    marketing_name: str = pydantic.Field(alias="marketingName")

    @classmethod
    def from_proto(cls, cabin_class: models_pb2.CabinClass) -> CabinClass:
        return cls(
            name=protobuf.enum_value_to_slug(
                descriptor=models_pb2.CabinClass.Type.DESCRIPTOR,
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


class Offer(models.BaseModel):
    identifier: str = pydantic.Field(alias="id")
    price: Price
    segment_details: Sequence[OfferSegmentDetails] = pydantic.Field(
        alias="segmentDetails",
    )

    @classmethod
    def from_proto(cls, offer: offer_models_pb2.Offer) -> Offer:
        return cls(
            id=offer.id,
            price=Price.from_proto(offer.price),
            segmentDetails=[
                OfferSegmentDetails.from_proto(segment_details)
                for segment_details in offer.segment_details
            ],
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
    operator: Optional[str] = None


class OfferSegment(models.BaseModel):
    ref: str
    legs: Sequence[OfferSegmentLeg]
    vendor: str
    operator: Optional[str] = None
    route_identifiers: RouteIdentifiers = pydantic.Field(alias="routeIdentifiers")

    @classmethod
    def from_proto(cls, segment: offer_models_pb2.OfferSegment) -> OfferSegment:
        return cls(
            ref=segment.id,
            legs=[OfferSegmentLeg.from_proto(leg) for leg in segment.legs],
            vendor=segment.vendor,
            operator=segment.operator or None,
            routeIdentifiers=RouteIdentifiers(
                vendor=segment.vehicle.number,
                operator=None,
            ),
        )


class OfferGroup(models.BaseModel):
    offers: Sequence[Offer]
    segments: Sequence[OfferSegment]

    @classmethod
    def from_proto(cls, offer_group: offer_models_pb2.OfferGroup) -> OfferGroup:
        return cls(
            offers=[Offer.from_proto(offer) for offer in offer_group.offers],
            segments=[
                OfferSegment.from_proto(segment) for segment in offer_group.segments
            ],
        )


class OrderResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        order: order_models_pb2.Order,
        request: requests.Request,
    ) -> OrderResource:
        return cls(
            id=order.id,
            type="orders",
            attributes={
                "orderResults": [
                    {
                        "offerId": order_result.offer_id,
                        "status": protobuf.enum_value_to_slug(
                            descriptor=order_models_pb2.OrderResult.Status.DESCRIPTOR,
                            enum_value=order_result.status,
                        ),
                    }
                    for order_result in order.order_results
                ],
                "passengers": [
                    {
                        "firstName": passenger.first_name,
                        "dateOfBirth": protobuf.protobuf_to_date(
                            passenger.date_of_birth,
                        ),
                        "title": protobuf.enum_value_to_slug(
                            descriptor=order_models_pb2.Passenger.Title.DESCRIPTOR,
                            enum_value=passenger.title,
                        ),
                        "lastName": passenger.last_name,
                        "gender": protobuf.enum_value_to_slug(
                            descriptor=order_models_pb2.Passenger.Gender.DESCRIPTOR,
                            enum_value=passenger.gender,
                        ),
                    }
                    for passenger in order.passengers
                ],
                "contactDetails": {
                    "address": {
                        "addressLines": list(
                            order.contact_details.address.address_lines,
                        ),
                        "regionCode": order.contact_details.address.region_code,
                        "revision": order.contact_details.address.revision,
                    },
                    "email": order.contact_details.email,
                    "phone": order.contact_details.phone.e164_number,
                },
            },
            relationships={},
            links={
                _SELF_HREF: "https://snowfall.se",
            },
        )


class PlaceResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        place: models_pb2.Place,
        request: requests.Request,
    ) -> PlaceResource:
        return cls(
            id=place.id,
            type="places",
            attributes={
                "countryCode": place.country_code.rjust(2, "X"),
                "iataCode": None,
                "latitude": place.coordinates.latitude,
                "longitude": place.coordinates.longitude,
                "name": place.name,
                "timeZone": place.time_zone,
            },
            relationships={
                "types": {
                    _RELATIONSHIPS_FIELD: [
                        models.ResourceIdentifier(
                            id=protobuf.enum_value_to_slug(
                                descriptor=models_pb2.Place.Type.DESCRIPTOR,
                                enum_value=place_type,
                            ),
                            type="place-types",
                        )
                        for place_type in place.types
                    ],
                },
            },
            links={
                _SELF_HREF: request.url_for(
                    "ViewPlace",
                    placeId=place.id,
                ),
            },
        )


class PlaceTypeResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        place_type: models_pb2.Place.Type.V,
        request: requests.Request,
    ) -> PlaceTypeResource:
        place_type_id = protobuf.enum_value_to_slug(
            descriptor=models_pb2.Place.Type.DESCRIPTOR,
            enum_value=place_type,
        )
        return cls(
            id=place_type_id,
            type="place-types",
            attributes={
                "name": place_type_id,
            },
            links={
                _SELF_HREF: request.url_for(
                    "ViewPlaceType",
                    placeTypeId=place_type_id,
                ),
            },
        )


class PassengerGenderResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        passenger_gender: order_models_pb2.Passenger.Gender.V,
        request: requests.Request,
    ) -> PassengerGenderResource:
        passenger_gender_id = protobuf.enum_value_to_slug(
            descriptor=order_models_pb2.Passenger.Gender.DESCRIPTOR,
            enum_value=passenger_gender,
        )
        return cls(
            id=passenger_gender_id,
            type="passenger-genders",
            attributes={
                "name": passenger_gender_id,
            },
            links={
                _SELF_HREF: request.url_for(
                    "ViewPassengerGender",
                    passengerGenderId=passenger_gender_id,
                ),
            },
        )


class PassengerTitleResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        passenger_title: order_models_pb2.Passenger.Title.V,
        request: requests.Request,
    ) -> PassengerTitleResource:
        passenger_title_id = protobuf.enum_value_to_slug(
            descriptor=order_models_pb2.Passenger.Title.DESCRIPTOR,
            enum_value=passenger_title,
        )
        return cls(
            id=passenger_title_id,
            type="passenger-titles",
            attributes={
                "name": passenger_title_id,
            },
            links={
                _SELF_HREF: request.url_for(
                    "ViewPassengerTitle",
                    passengerTitleId=passenger_title_id,
                ),
            },
        )


class SegmentResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        segment: models_pb2.SegmentReference,
        request: requests.Request,
    ) -> SegmentResource:
        return cls(
            id=segment.id,
            type="segments",
            attributes={},
            relationships={
                "legs": {
                    _RELATIONSHIPS_FIELD: [
                        models.ResourceIdentifier(
                            id=leg_id,
                            type="legs",
                        )
                        for leg_id in segment.leg_ids
                    ],
                },
            },
            links={
                _SELF_HREF: request.url_for(
                    "ViewSegment",
                    segmentId=segment.id,
                ),
            },
        )


class LegResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        leg: models_pb2.Leg,
        request: requests.Request,
    ) -> LegResource:
        return cls(
            id=leg.id,
            type="legs",
            attributes={
                "departureAt": protobuf.protobuf_to_datetime(
                    leg.departure_at,
                ).astimezone(zoneinfo.ZoneInfo(leg.origin.time_zone)),
                "arrivalAt": protobuf.protobuf_to_datetime(
                    leg.arrival_at,
                ).astimezone(zoneinfo.ZoneInfo(leg.destination.time_zone)),
                "operator": leg.agency_name,
                "origin": Point.from_proto(leg.origin),
                "destination": Point.from_proto(leg.destination),
            },
            relationships={
                "type": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=protobuf.enum_value_to_slug(
                            descriptor=models_pb2.Schedule.Type.DESCRIPTOR,
                            enum_value=leg.type,
                        ),
                        type="leg-types",
                    ),
                },
            },
            links={
                _SELF_HREF: request.url_for(
                    "ViewLeg",
                    legId=leg.id,
                ),
            },
        )


class LegTypeResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        schedule_type: models_pb2.Schedule.Type.V,
        request: requests.Request,
    ) -> LegTypeResource:
        schedule_type_id = protobuf.enum_value_to_slug(
            descriptor=models_pb2.Schedule.Type.DESCRIPTOR,
            enum_value=schedule_type,
        )
        return cls(
            id=schedule_type_id,
            type="leg-types",
            attributes={
                "name": schedule_type_id,
            },
            links={
                _SELF_HREF: request.url_for(
                    "ViewLegType",
                    legTypeId=schedule_type_id,
                ),
            },
        )


class TripResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        trip: models_pb2.TripReference,
        request: requests.Request,
    ) -> TripResource:
        return cls(
            id=trip.id,
            type="trips",
            attributes={},
            relationships={
                "segments": {
                    _RELATIONSHIPS_FIELD: [
                        models.ResourceIdentifier(
                            id=segment.id,
                            type="segments",
                        )
                        for segment in trip.segments
                    ],
                },
            },
            links={
                _SELF_HREF: request.url_for(
                    "ViewTrip",
                    tripId=trip.id,
                ),
            },
        )


class TripSearchResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        trip_search: trips_pb2.TripSearch,
        request: requests.Request,
    ) -> TripSearchResource:
        return cls(
            id=trip_search.id,
            type="trip-searches",
            attributes={
                "expiresAt": protobuf.protobuf_to_datetime(
                    trip_search.expires_at,
                ),
                "departureAfter": protobuf.protobuf_to_datetime(
                    trip_search.departure_after,
                ),
            },
            relationships={
                "origin": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=trip_search.origin.id,
                        type="places",
                    ),
                },
                "destination": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=trip_search.destination.id,
                        type="places",
                    ),
                },
            },
            links={
                _SELF_HREF: request.url_for(
                    "ViewTripSearch",
                    tripSearchId=trip_search.id,
                ),
            },
        )


class TripOfferSearchResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        offer_search: offer_models_pb2.OfferSearch,
        offers: Sequence[offer_models_pb2.OfferAggregateMapping],
        request: requests.Request,
    ) -> TripOfferSearchResource:
        return cls(
            id=offer_search.id,
            type="trip-offer-searches",
            attributes=cls._get_attributes(offer_search),
            relationships={
                "offers": {
                    _RELATIONSHIPS_FIELD: [
                        models.ResourceIdentifier(
                            id=offer.id,
                            type=_OFFERS_TYPE,
                        )
                        for offer in offers
                    ],
                },
            },
            links={
                _SELF_HREF: "https://snowfall.se",
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
        }

        if offer_search.trip.HasField("loyalty_card"):
            attributes["loyalty"] = {
                "airlineIata": offer_search.trip.loyalty_card.airline_iata,
                "number": offer_search.trip.loyalty_card.number,
                "firstName": offer_search.trip.loyalty_card.first_name,
                "lastName": offer_search.trip.loyalty_card.last_name,
            }

        return attributes
