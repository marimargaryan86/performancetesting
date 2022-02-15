import datetime
import itertools
import uuid
from typing import AsyncIterator, Iterator, Optional

from google.protobuf import timestamp_pb2

from snowfall.common.v1alpha import models_pb2
from snowfall.format.gtfs import datetimes, enums, feed, models
from snowfall.geodata import geocoding
from snowfall.transport import amqp


class SchedulesGenerator(object):
    def __init__(
        self,
        geocoder: geocoding.ReverseGeocoder,
    ):
        self._geocoder = geocoder

    async def generate(
        self,
        gtfs_feed: feed.FeedDecorator,
    ) -> AsyncIterator[models_pb2.Schedule]:
        stop_times_by_trip = itertools.groupby(
            gtfs_feed.feed.stop_times,
            key=lambda st: st.trip_id,
        )

        for trip_id, stop_times in stop_times_by_trip:
            trip = gtfs_feed.get_trip_by_id(trip_id)

            async for schedule in self._generate_for_trip(gtfs_feed, trip, stop_times):
                yield schedule

    async def _generate_for_trip(
        self,
        gtfs_feed: feed.FeedDecorator,
        trip: models.Trip,
        stop_times: Iterator[models.StopTime],
    ) -> AsyncIterator[models_pb2.Schedule]:
        service_dates = gtfs_feed.get_service_dates_by_service_id(trip.service_id)
        sorted_stop_times = sorted(stop_times, key=lambda st: st.stop_sequence)

        for service_date in service_dates:
            schedule = await self._generate_for_trip_on_service_date(
                gtfs_feed,
                trip,
                service_date,
                sorted_stop_times,
            )

            if schedule:
                yield schedule

    async def _generate_for_trip_on_service_date(
        self,
        gtfs_feed: feed.FeedDecorator,
        trip: models.Trip,
        service_date: datetime.date,
        stop_times: list[models.StopTime],
    ) -> Optional[models_pb2.Schedule]:
        stops = [
            await self._generate_stop(
                gtfs_feed,
                service_date,
                sequence,
                stop_time,
            )
            for sequence, stop_time in enumerate(stop_times)
            if stop_time.pickup_type == 0 or stop_time.drop_off_type == 0
        ]

        if not stops:
            return None

        route = gtfs_feed.get_route_by_id(trip.route_id)
        id_parts = (trip.trip_id, service_date.isoformat())

        return models_pb2.Schedule(
            id=str(uuid.uuid5(gtfs_feed.namespace, "\x00".join(id_parts))),
            name=route.route_short_name or route.route_long_name or "",
            stops=stops,
            agency_name=gtfs_feed.get_agency_by_id(route.agency_id or "").agency_name,
            source_ref=gtfs_feed.feed.ref,
            type=enums.gtfs_type_to_schedule_type(route.route_type),
        )

    async def _generate_stop(
        self,
        gtfs_feed: feed.FeedDecorator,
        service_date: datetime.date,
        sequence: int,
        stop_time: models.StopTime,
    ) -> models_pb2.Stop:
        trip = gtfs_feed.get_trip_by_id(stop_time.trip_id)
        stop = gtfs_feed.get_stop_by_id(stop_time.stop_id)
        id_parts = (trip.trip_id, service_date.isoformat(), str(sequence))
        departure_at = None
        arrival_at = None

        if stop_time.pickup_type == 0 and stop_time.departure_time:
            departure_at = timestamp_pb2.Timestamp()
            departure_at.FromDatetime(
                datetimes.create_datetime(
                    service_date,
                    stop_time.departure_time,
                    gtfs_feed.time_zone,
                ),
            )

        if stop_time.drop_off_type == 0 and stop_time.arrival_time:
            arrival_at = timestamp_pb2.Timestamp()
            arrival_at.FromDatetime(
                datetimes.create_datetime(
                    service_date,
                    stop_time.arrival_time,
                    gtfs_feed.time_zone,
                ),
            )

        return models_pb2.Stop(
            id=str(uuid.uuid5(gtfs_feed.namespace, "\x00".join(id_parts))),
            departure_at=departure_at,
            arrival_at=arrival_at,
            point=models_pb2.Point(
                ref=stop.stop_id,
                name=stop.stop_name or "",
                coordinates=models_pb2.Coordinates(
                    latitude=stop.stop_lat or 0,
                    longitude=stop.stop_lon or 0,
                ),
                time_zone=await self._geocoder.get_time_zone(
                    stop.stop_lat or 0,
                    stop.stop_lon or 0,
                ),
            ),
            order=sequence,
        )


async def produce_schedules(
    connection: amqp.Connection,
    generator: AsyncIterator[models_pb2.Schedule],
) -> None:
    producer = await amqp.create_producer(
        conn=connection,
        exchange_name="schedules",
    )

    async for schedule in generator:
        await producer.publish(schedule, "schedule.import")
