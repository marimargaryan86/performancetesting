import asyncio
from typing import Any, Mapping, Sequence

from snowfall.junction.mobile_api import repository
from snowfall.vendor.junction import client

_TRIPS_POLLING_TIMEOUT = 20
_TRIPS_POLLING_INTERVAL = 3
_RELATIONSHIPS_ACCESSOR = "relationships"
_DATA_ACCESSOR = "data"


async def _save_new_trip(
    trip_search_id: str,
    trip: Mapping[str, Any],
    trip_searches_repository: repository.TripSearchesRepository,
    trips_repository: repository.TripsRepository,
) -> None:
    trip = dict(trip)
    trip[_RELATIONSHIPS_ACCESSOR]["segments"] = trip[_RELATIONSHIPS_ACCESSOR][
        "segments"
    ].pop(_DATA_ACCESSOR)
    trip["attributes"] = trip.pop(_RELATIONSHIPS_ACCESSOR)
    await trip_searches_repository.update_trip(trip_search_id, trip)
    await trips_repository.create_trip(trip)


async def _get_new_trips(
    trip_search_id: str,
    junction_client: client.JunctionClient,
    trip_searches_repository: repository.TripSearchesRepository,
) -> Sequence[Mapping[str, Any]]:
    trips_response = await junction_client.get_trips_by_trip_search_id(
        trip_search_id,
        limit=100,
    )

    trips: Sequence[dict[str, Any]] = trips_response[_DATA_ACCESSOR]

    return [
        trip
        for trip in trips
        if trip["id"] not in await trip_searches_repository.get_trip_ids(trip_search_id)
    ]


async def poll_trips(
    trip_search_id: str,
    trip_searches_repository: repository.TripSearchesRepository,
    trips_repository: repository.TripsRepository,
    junction_client: client.JunctionClient,
) -> None:
    time_spent = 0
    while time_spent <= _TRIPS_POLLING_TIMEOUT:
        new_trips = await _get_new_trips(
            trip_search_id,
            junction_client,
            trip_searches_repository,
        )

        for trip in new_trips:
            for segment in trip["relationships"]["segments"][_DATA_ACCESSOR]:
                legs = await junction_client.get_legs_by_segment_id(
                    segment["id"],
                    limit=100,
                )
                legs = legs[_DATA_ACCESSOR]
                segment["legs"] = legs

            await _save_new_trip(
                trip_search_id,
                trip,
                trip_searches_repository,
                trips_repository,
            )

        await asyncio.sleep(_TRIPS_POLLING_INTERVAL)
        time_spent += _TRIPS_POLLING_INTERVAL
