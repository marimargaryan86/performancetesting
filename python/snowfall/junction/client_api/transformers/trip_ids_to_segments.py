import collections
import itertools
from typing import Sequence

from snowfall.adapter import schedules, trips
from snowfall.common.v1alpha import models_pb2


class MissingTripsError(Exception):
    """Raised when not all trips where found."""


class TripIdsToSegments(object):
    def __init__(
        self,
        trips_client: trips.Client,
        schedules_client: schedules.Client,
    ):
        self._trips = trips_client
        self._schedules = schedules_client

    async def transform(self, trip_ids: list[str]) -> list[models_pb2.Segment]:
        trips_page = await self._trips.find_by_ids(
            trip_ids,
            limit=len(trip_ids),
        )

        found_trip_ids = [trip.id for trip in trips_page.trips]

        if collections.Counter(trip_ids) != collections.Counter(found_trip_ids):
            raise MissingTripsError("Could not find all trips")

        schedule_ids = {
            segment.schedule_id
            for trip in trips_page.trips
            for segment in trip.segments
        }

        schedules_page = await self._schedules.find_by_ids(
            list(schedule_ids),
            limit=len(schedule_ids),
        )

        stops_map = {
            schedule.id: schedule.stops for schedule in schedules_page.schedules
        }

        return [
            models_pb2.Segment(
                id=segment.id,
                stops=filter_stops_in_segment_reference(
                    segment,
                    stops_map[segment.schedule_id],
                ),
            )
            for trip in trips_page.trips
            for segment in trip.segments
        ]


def filter_stops_in_segment_reference(
    segment: models_pb2.SegmentReference,
    stops: Sequence[models_pb2.Stop],
) -> list[models_pb2.Stop]:
    return list(
        reversed(
            list(
                itertools.dropwhile(
                    lambda stop: stop.id != segment.destination_stop_id,
                    reversed(
                        list(
                            itertools.dropwhile(
                                lambda stop: stop.id != segment.origin_stop_id,
                                sorted(stops, key=lambda stop: stop.order),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )
