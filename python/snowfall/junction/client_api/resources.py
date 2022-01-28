from __future__ import annotations

from starlette import requests

from snowfall.adapter import places, trip_searches, trips
from snowfall.junction.client_api import models


class PlaceResource(models.Resource):
    @classmethod
    async def from_data_class(
        cls,
        place: places.Place,
        request: requests.Request,
    ) -> PlaceResource:
        return cls(
            id=str(place.identifier),
            type="places",
            attributes={
                "countryCode": place.country_code,
                "iataCode": None,
                "latitude": place.latitude,
                "longitude": place.longitude,
                "name": place.name,
                "timeZone": place.time_zone,
                "type": "stop",
            },
            links={
                "self": request.url_for(
                    "ViewPlace",
                    placeId=place.identifier,
                ),
            },
        )


class TripResource(models.Resource):
    @classmethod
    async def from_data_class(
        cls,
        trip: trips.Trip,
        request: requests.Request,
    ) -> TripResource:
        return cls(
            id=str(trip.identifier),
            type="trips",
            attributes={
                "expiresAt": trip.expires_at,
            },
            relationships={
                "segments": {
                    "data": [],
                },
            },
            links={
                "self": request.url_for(
                    "ViewTrip",
                    tripId=trip.identifier,
                ),
            },
        )


class TripSearchResource(models.Resource):
    @classmethod
    async def from_data_class(
        cls,
        trip_search: trip_searches.TripSearch,
        request: requests.Request,
    ) -> TripSearchResource:
        return cls(
            id=str(trip_search.identifier),
            type="trip-searches",
            attributes={
                "expiresAt": trip_search.expires_at,
                "departureAfter": trip_search.departure_after,
            },
            relationships={
                "origin": {
                    "data": {
                        "id": str(trip_search.origin.identifier),
                        "type": "places",
                    },
                },
                "destination": {
                    "data": {
                        "id": str(trip_search.destination.identifier),
                        "type": "places",
                    },
                },
            },
            links={
                "self": request.url_for(
                    "ViewTripSearch",
                    tripSearchId=trip_search.identifier,
                ),
            },
        )
