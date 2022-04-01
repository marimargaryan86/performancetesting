from typing import Sequence

from snowfall.adapter import legs, trips
from snowfall.common.v1alpha import models_pb2


class MissingTripsError(Exception):
    """Raised when not all trips where found."""


class TripIdsToSegments(object):
    def __init__(
        self,
        legs_client: legs.Client,
        trips_client: trips.Client,
    ):
        self._legs = legs_client
        self._trips = trips_client

    async def transform(self, trip_ids: Sequence[str]) -> list[models_pb2.Segment]:
        trips_list = (
            await self._trips.find_by_ids(
                trip_ids,
                limit=len(trip_ids),
            )
        ).trips

        if len(trip_ids) != len(trips_list):
            raise MissingTripsError("Could not find all trips")

        segments = [segment for trip in trips_list for segment in trip.segments]
        leg_ids = {leg_id for segment in segments for leg_id in segment.leg_ids}
        legs_list = (
            await self._legs.find_by_ids(
                list(leg_ids),
                limit=len(leg_ids),
            )
        ).legs

        if len(leg_ids) != len(legs_list):
            raise MissingTripsError("Could not find all trips")

        legs_map = {leg.id: leg for leg in legs_list}

        return [
            models_pb2.Segment(
                id=segment.id,
                legs=[legs_map[leg_id] for leg_id in segment.leg_ids],
            )
            for trip in trips_list
            for segment in trip.segments
        ]
