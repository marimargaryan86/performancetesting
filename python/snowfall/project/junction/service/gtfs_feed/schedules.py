import dataclasses
import datetime
import uuid
import zoneinfo
from typing import AsyncIterator, Optional, Sequence

import more_itertools
from aio_pika import abc
from google.protobuf import timestamp_pb2

from snowfall.project.junction.service.gtfs_feed import importer
from snowfall.service.geodata.v1 import geocoding_pb2, geocoding_pb2_grpc
from snowfall.stdlib.format.gtfs import constants, datetimes, enums, models
from snowfall.stdlib.transport import amqp
from snowfall.stdlib.v1alpha import latlng_pb2, models_pb2


@dataclasses.dataclass  # noqa: SF10
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
        geocoder: geocoding_pb2_grpc.GeocodingServiceStub,
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
            [agency async for agency in await self._collection.agencies.all_()][
                0
            ].agency_timezone,
        )

        # todo: creating a context like this is fugly, should be improved.
        context = _ScheduleContext(
            agency=models.Agency.construct(
                agency_name="",
                agency_url="https://example.com/",  # type: ignore[arg-type]
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
        trips = await self._collection.trips.all_()

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
                [
                    stop_time
                    for stop_time in stop_times
                    if stop_time.pickup_type == 0 or stop_time.drop_off_type == 0
                ],
            )

            if schedule:
                yield schedule

    async def _generate_for_trip_on_service_date(
        self,
        context: _ScheduleContext,
        service_date: datetime.date,
        stop_times: Sequence[models.StopTime],
    ) -> Optional[models_pb2.Schedule]:
        stops = [
            await self._generate_stop(
                context,
                service_date,
                sequence,
                stop_time,
            )
            for sequence, stop_time in enumerate(stop_times)
        ]

        if not stops:
            return None

        schedule = models_pb2.Schedule(
            id=str(
                uuid.uuid5(
                    self._namespace,
                    "\x00".join((context.trip.trip_id, service_date.isoformat())),
                ),
            ),
            name=context.route.route_short_name or context.route.route_long_name or "",
            stops=stops,
            agency_name=context.agency.agency_name,
            source_ref=self._ref,
            type=context.route_type,
        )

        return _append_legs(schedule)

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
                time_zone=(
                    await self._geocoder.TimeZoneLookup(
                        geocoding_pb2.TimeZoneLookupRequest(
                            coordinates=latlng_pb2.LatLng(
                                latitude=stop.stop_lat or 0,
                                longitude=stop.stop_lon or 0,
                            ),
                        ),
                    )
                ).time_zone.id,
            ),
            order=sequence,
        )

    async def _set_trip_contexts(
        self,
        context: _ScheduleContext,
        stop_times: Sequence[models.StopTime],
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


def _append_legs(
    schedule: models_pb2.Schedule,
) -> models_pb2.Schedule:
    schedule_id = uuid.UUID(schedule.id)

    schedule.legs.extend(
        [
            models_pb2.Leg(
                id=str(
                    uuid.uuid5(
                        schedule_id,
                        "\x00".join((origin.id, destination.id)),
                    ),
                ),
                origin=origin.point,
                destination=destination.point,
                departure_at=origin.departure_at,
                arrival_at=destination.arrival_at,
                type=schedule.type,
                agency_name=schedule.agency_name,
            )
            for origin, destination in more_itertools.pairwise(schedule.stops)
        ],
    )

    return schedule


async def produce_schedules(
    connection: abc.AbstractConnection,
    generator: SchedulesGenerator,
) -> None:
    producer = amqp.Producer(
        connection=connection,
        exchange=amqp.Exchange("schedules"),
    )

    async for schedule in generator.generate():
        await producer.publish(schedule, "schedule.import")
