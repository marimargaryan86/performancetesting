from __future__ import annotations

from typing import Any, Mapping

from snowfall.junction.mobile_api.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models


class PlaceResource(models.Resource):
    """Resource for a place."""


class OrderResource(models.Resource):
    @classmethod
    def from_mongo(
        cls,
        order: Mapping[str, Any],
    ) -> OrderResource:
        return cls(**order)


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
