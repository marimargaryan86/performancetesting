import dataclasses
import datetime
import uuid
import zoneinfo
from typing import AsyncIterator, Optional

import pydantic
from google.protobuf import timestamp_pb2

from snowfall.common.v1alpha import models_pb2
from snowfall.format.gtfs import constants, datetimes, enums, models
from snowfall.geodata import geocoding
from snowfall.junction.gtfs_feed import importer
from snowfall.transport import amqp


@dataclasses.dataclass
class _ScheduleContext(object):
    agency: models.Agency
    route: models.Route
    route_type: "models_pb2.Schedule.Type.V"
    trip: models.Trip
    service_dates: set[datetime.date] = dataclasses.field(default_factory=set)
    service_id: str = ""
    stop_ids: set[str] = dataclasses.field(default_factory=set)
    stops: dict[str, models.Stop] = dataclasses.field(default_factory=dict)


class SchedulesGenerator(object):
    def __init__(
        self,
        geocoder: geocoding.ReverseGeocoder,
        ref: str,
        repository_collection: importer.RepositoryCollection,
    ):
        self._collection = repository_collection
        self._geocoder = geocoder
        self._namespace = uuid.uuid5(constants.NAMESPACE, ref)
        self._ref = ref
        self._time_zone = zoneinfo.ZoneInfo("UTC")

    async def generate(self) -> AsyncIterator[models_pb2.Schedule]:
        self._time_zone = zoneinfo.ZoneInfo(
            [
                agency
                async for agency in await self._collection.agencies.find_with_cursor()
            ][0].agency_timezone,
        )

        # todo: creating a context like this is fugly, should be improved.
        context = _ScheduleContext(
            agency=models.Agency.construct(
                agency_name="",
                agency_url=pydantic.HttpUrl("https://example.com/"),
                agency_timezone="",
            ),
            route=models.Route.construct(route_id="", route_type=0),
            route_type=models_pb2.Schedule.TYPE_UNSPECIFIED,
            trip=models.Trip.construct(
                route_id="",
                service_id="",
                trip_id="",
                wheelchair_accessible=0,
                bikes_allowed=0,
            ),
        )
        trips = await self._collection.trips.find_with_cursor()

        trips.sort(("route_id", 1), ("service_id", 1))

        async for trip in trips:
            context.trip = trip

            if not context.route or context.route.route_id != trip.route_id:
                context.route = await self._collection.routes.get_by_id(trip.route_id)
                context.route_type = enums.gtfs_type_to_schedule_type(
                    context.route.route_type,
                )

            if context.route_type == models_pb2.Schedule.TYPE_UNSPECIFIED:
                continue

            async for schedule in self._generate_for_trip(context):
                yield schedule

    async def _generate_for_trip(
        self,
        context: _ScheduleContext,
    ) -> AsyncIterator[models_pb2.Schedule]:
        stop_times = sorted(
            [
                st
                async for st in await self._collection.stop_times.find_by_trip_id(
                    context.trip.trip_id,
                )
            ],
            key=lambda st: st.stop_sequence,
        )

        await self._set_trip_contexts(context, stop_times)

        for service_date in context.service_dates:
            schedule = await self._generate_for_trip_on_service_date(
                context,
                service_date,
                stop_times,
            )

            if schedule:
                yield schedule

    async def _generate_for_trip_on_service_date(
        self,
        context: _ScheduleContext,
        service_date: datetime.date,
        stop_times: list[models.StopTime],
    ) -> Optional[models_pb2.Schedule]:
        stops = [
            await self._generate_stop(
                context,
                service_date,
                sequence,
                stop_time,
            )
            for sequence, stop_time in enumerate(stop_times)
            if stop_time.pickup_type == 0 or stop_time.drop_off_type == 0
        ]

        if not stops:
            return None

        id_parts = (context.trip.trip_id, service_date.isoformat())

        return models_pb2.Schedule(
            id=str(uuid.uuid5(self._namespace, "\x00".join(id_parts))),
            name=context.route.route_short_name or context.route.route_long_name or "",
            stops=stops,
            agency_name=context.agency.agency_name,
            source_ref=self._ref,
            type=context.route_type,
        )

    async def _generate_stop(
        self,
        context: _ScheduleContext,
        service_date: datetime.date,
        sequence: int,
        stop_time: models.StopTime,
    ) -> models_pb2.Stop:
        stop = context.stops[stop_time.stop_id]
        id_parts = (context.trip.trip_id, service_date.isoformat(), str(sequence))
        departure_at = None
        arrival_at = None

        if stop_time.pickup_type == 0 and stop_time.departure_time:
            departure_at = timestamp_pb2.Timestamp()
            departure_at.FromDatetime(
                datetimes.create_datetime(
                    service_date,
                    stop_time.departure_time,
                    self._time_zone,
                ),
            )

        if stop_time.drop_off_type == 0 and stop_time.arrival_time:
            arrival_at = timestamp_pb2.Timestamp()
            arrival_at.FromDatetime(
                datetimes.create_datetime(
                    service_date,
                    stop_time.arrival_time,
                    self._time_zone,
                ),
            )

        return models_pb2.Stop(
            id=str(uuid.uuid5(self._namespace, "\x00".join(id_parts))),
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

    async def _set_trip_contexts(
        self,
        context: _ScheduleContext,
        stop_times: list[models.StopTime],
    ) -> None:
        if context.trip.service_id != context.service_id:
            context.service_dates = await datetimes.calculate_serviceable_dates(
                await self._collection.calendars.find_by_service_id(
                    context.trip.service_id,
                ),
                await self._collection.calendar_dates.find_by_service_id(
                    context.trip.service_id,
                ),
            )
            context.service_id = context.trip.service_id

        if not context.agency or context.agency.agency_id != context.route.agency_id:
            context.agency = await self._collection.agencies.get_by_id(
                context.route.agency_id or "",
            )

        stop_ids = {st.stop_id for st in stop_times}

        if context.stop_ids != stop_ids:
            context.stop_ids = stop_ids
            context.stops = {
                stop.stop_id: stop
                async for stop in await self._collection.stops.find_by_ids(*stop_ids)
            }


async def produce_schedules(
    connection: amqp.Connection,
    generator: SchedulesGenerator,
) -> None:
    producer = await amqp.create_producer(
        conn=connection,
        exchange_name="schedules",
    )

    async for schedule in generator.generate():
        await producer.publish(schedule, "schedule.import")
