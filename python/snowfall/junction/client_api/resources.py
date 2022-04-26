from __future__ import annotations

import uuid
from typing import Any, Sequence

from starlette import requests

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.client_api import models
from snowfall.junction.offers.v1alpha import offers_pb2
from snowfall.junction.orders.v1alpha import models_pb2 as orders_models_pb2
from snowfall.junction.trips.v1alpha import trips_pb2
from snowfall.stdlib.format import protobuf

_SELF_HREF = "self"
_RELATIONSHIPS_FIELD = "data"
_OFFERS_TYPE = "offers"


class OfferResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        offer: offers_pb2.Offer,
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
        offer: offers_pb2.Offer,
    ) -> dict[str, Any]:
        first_expiring_offer = min(
            offer.results,
            key=lambda offer_result: offer_result.expires_at.seconds,
        )

        return {
            "expiresAt": protobuf.protobuf_to_datetime(first_expiring_offer.expires_at),
            "price": str(
                sum(
                    offer_result.offers[0].price.amount
                    for offer_result in offer.results
                )
                / 100,
            ),
            "currency": first_expiring_offer.offers[0].price.currency,
        }


class OrderResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        order: orders_models_pb2.Order,
        request: requests.Request,
    ) -> OrderResource:
        return cls(
            id=order.id,
            type="orders",
            attributes={
                "offers": {
                    _RELATIONSHIPS_FIELD: [
                        OfferResource.from_proto(offer, request)
                        for offer in order.offers
                    ],
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
                "countryCode": place.country_code,
                "iataCode": None,
                "latitude": place.coordinates.latitude,
                "longitude": place.coordinates.longitude,
                "name": place.name,
                "timeZone": place.time_zone,
                "type": "stop",
            },
            links={
                _SELF_HREF: request.url_for(
                    "ViewPlace",
                    placeId=place.id,
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
                    _RELATIONSHIPS_FIELD: [],
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
                ),
                "arrivalAt": protobuf.protobuf_to_datetime(
                    leg.arrival_at,
                ),
                "operator": leg.agency_name,
                "origin": {
                    "ref": leg.origin.ref,
                    "name": leg.origin.name,
                    "latitude": leg.origin.coordinates.latitude,
                    "longitude": leg.origin.coordinates.longitude,
                    "timeZone": leg.origin.time_zone,
                },
                "destination": {
                    "ref": leg.destination.ref,
                    "name": leg.destination.name,
                    "latitude": leg.destination.coordinates.latitude,
                    "longitude": leg.destination.coordinates.longitude,
                    "timeZone": leg.destination.time_zone,
                },
            },
            relationships={
                "type": {
                    _RELATIONSHIPS_FIELD: {
                        "id": uuid.uuid4(),  # TODO: use schedule type
                        "type": "leg-types",
                    },
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
            models_pb2.Schedule.Type.DESCRIPTOR,
            schedule_type,
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
                        SegmentResource.from_proto(
                            segment=segment,
                            request=request,
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
        offer_search: offers_pb2.OfferSearch,
        offers: Sequence[offers_pb2.OfferAggregate],
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
        offer_search: offers_pb2.OfferSearch,
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
