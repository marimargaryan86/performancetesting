from __future__ import annotations

from starlette import requests

from snowfall.common.v1alpha import models_pb2
from snowfall.format import protobuf
from snowfall.junction.client_api import models
from snowfall.junction.planner.v1 import planner_pb2
from snowfall.junction.trips.v1alpha import trips_pb2


class PlaceResource(models.Resource):
    @classmethod
    async def from_proto(
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
                "self": request.url_for(
                    "ViewPlace",
                    placeId=place.id,
                ),
            },
        )


class TripResource(models.Resource):
    @classmethod
    async def from_proto(
        cls,
        trip: planner_pb2.TripReference,
        request: requests.Request,
    ) -> TripResource:
        return cls(
            id=trip.id,
            type="trips",
            attributes={},
            relationships={
                "segments": {
                    "data": [],
                },
            },
            links={
                "self": request.url_for(
                    "ViewTrip",
                    tripId=trip.id,
                ),
            },
        )


class TripSearchResource(models.Resource):
    @classmethod
    async def from_proto(
        cls,
        trip_search: trips_pb2.TripSearch,
        request: requests.Request,
    ) -> TripSearchResource:
        return cls(
            id=trip_search.id,
            type="trip-searches",
            attributes={
                "expiresAt": await protobuf.protobuf_to_datetime(
                    trip_search.expires_at,
                ),
                "departureAfter": await protobuf.protobuf_to_datetime(
                    trip_search.departure_after,
                ),
            },
            relationships={
                "origin": {
                    "data": {
                        "id": trip_search.origin.id,
                        "type": "places",
                    },
                },
                "destination": {
                    "data": {
                        "id": trip_search.destination.id,
                        "type": "places",
                    },
                },
            },
            links={
                "self": request.url_for(
                    "ViewTripSearch",
                    tripSearchId=trip_search.id,
                ),
            },
        )
