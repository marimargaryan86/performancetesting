from __future__ import annotations

import enum
from typing import Any, Mapping

from snowfall.project.junction.service.mobile_api.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models

_RELATIONSHIPS_FIELD = "data"


class OrderResource(models.Resource):
    @classmethod
    def from_mongo(
        cls,
        order: Mapping[str, Any],
    ) -> OrderResource:
        return cls(**order)


class OrderStatus(enum.Enum):
    unspecified = "unspecified"
    pending = "pending"
    confirmed = "confirmed"
    rejected = "rejected"
    not_ticketed = "not_ticketed"
    error = "error"
    timeout = "timeout"


class TripSearchResource(models.Resource):
    @classmethod
    def from_mongo(
        cls,
        trip_search: Mapping[str, Any],
    ) -> TripSearchResource:
        return cls(**trip_search)


class TripSearchTripsResource(models.Resource):
    @classmethod
    def from_mongo(
        cls,
        trip_search_trip: Mapping[str, Any],
    ) -> TripSearchTripsResource:
        return cls(**trip_search_trip)


class UserResource(models.Resource):
    @classmethod
    def from_proto(cls, user: models_pb2.User) -> UserResource:
        return cls(
            id=user.id,
            type="users",
            attributes={
                "name": user.name,
                "email": user.email,
                "phone": user.phone.e164_number,
                "created": protobuf.protobuf_to_datetime(
                    user.created_at,
                ),
                "updated": protobuf.protobuf_to_datetime(
                    user.updated_at,
                ),
            },
        )


class OfferSearchOffersResource(models.Resource):
    @classmethod
    def from_dict(
        cls,
        offer_search_offer: Mapping[str, Any],
    ) -> OfferSearchOffersResource:
        return cls(**offer_search_offer)


class PlaceResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        place: models_pb2.Place,
    ) -> PlaceResource:
        return cls(
            id=place.id,
            type="places",
            attributes={
                "countryCode": place.country_code,
                "countryName": place.country_name,
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
        )
