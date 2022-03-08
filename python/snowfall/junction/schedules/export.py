import datetime
import hashlib
import pathlib
import pickle  # nosec
from typing import Literal

import aiofiles
import structlog
from aiofiles.threadpool import binary
from h3.api import numpy_int as h3

from snowfall.common.v1alpha import models_pb2
from snowfall.format import protobuf
from snowfall.junction.planner.v1alpha import schedules_pb2
from snowfall.junction.schedules import schedules
from snowfall.persistence import redis

_FILE_MODE: Literal["wb"] = "wb"
_MIN_TRANSFER_TIME = 25 * 60  # noqa: WPS432 - todo: calculate somehow?
_START_SEQUENCE = -1


class State(object):
    def __init__(self, client: redis.Client, repository: schedules.ScheduleRepository):
        self._logger = structlog.get_logger(__name__)
        self._repository = repository
        self._redis = client

    async def mark_as_completed(self) -> None:
        await self._redis.set_(
            "last_executed_at",
            str(datetime.datetime.now().timestamp()),
        )

    async def should_run_export(self) -> bool:
        actual = await self._repository.get_last_updated_at()
        expected = await self._get_timestamp_from_redis("last_seen_update_at")

        if actual != expected:
            await self._redis.set_(
                "last_seen_update_at",
                str(actual.timestamp()),
            )

            self._logger.info("Data update seemingly in progress, skipping.")
            return False

        last_executed_at = await self._get_timestamp_from_redis("last_executed_at")

        if last_executed_at > actual:
            self._logger.info("No new data available for export, skipping.")
            return False

        self._logger.info("Export started.")
        return True

    async def _get_timestamp_from_redis(self, redis_key: str) -> datetime.datetime:
        redis_value = await self._redis.get(redis_key)

        if not redis_value:
            return datetime.datetime.fromtimestamp(0, tz=datetime.timezone.utc)

        return datetime.datetime.fromtimestamp(
            float(redis_value.decode()),
            tz=datetime.timezone.utc,
        )


class Exporter(object):  # noqa: WPS214
    def __init__(self, client: redis.Client, repository: schedules.ScheduleRepository):
        self._repository = repository
        self._redis = client
        self._state = State(client, repository)
        self._route_sequence = _START_SEQUENCE
        self._route_stop_sequence = _START_SEQUENCE
        self._stop_sequence = _START_SEQUENCE
        self._schedule_sequence = _START_SEQUENCE
        self._schedule_stop_sequence = _START_SEQUENCE
        self._routes = client.hash_("routes")
        self._route_sequences = client.hash_("route_sequences")
        self._stops = client.hash_("stops")
        self._stop_sequences = client.hash_("stop_sequences")

    async def export(self, path: pathlib.Path) -> None:  # noqa: WPS217
        if not await self._state.should_run_export():
            return

        await self._redis.delete("*")

        self._route_sequence = _START_SEQUENCE
        self._route_stop_sequence = _START_SEQUENCE
        self._stop_sequence = _START_SEQUENCE
        self._schedule_sequence = _START_SEQUENCE
        self._schedule_stop_sequence = _START_SEQUENCE

        async with aiofiles.open(
            str(path.joinpath("route_stops.bin")),
            mode=_FILE_MODE,
        ) as route_stops_f:
            async with aiofiles.open(
                str(path.joinpath("schedules.bin")),
                mode=_FILE_MODE,
            ) as schedules_f:
                async with aiofiles.open(
                    str(path.joinpath("schedule_stops.bin")),
                    mode=_FILE_MODE,
                ) as schedule_stops_f:
                    await self._store_schedules(
                        route_stops_f,
                        schedules_f,
                        schedule_stops_f,
                    )

        for generator in (self._store_routes(path), self._store_stops(path)):
            await generator

        async with aiofiles.open(
            str(path.joinpath("transfers.bin")),
            mode=_FILE_MODE,
        ) as transfers_f:
            await transfers_f.write(b"")

        await self._redis.delete("*")
        await self._state.mark_as_completed()

    async def _store_schedules(
        self,
        route_stops_f: binary.AsyncBufferedIOBase,
        schedules_f: binary.AsyncBufferedIOBase,
        schedule_stops_f: binary.AsyncBufferedIOBase,
    ) -> None:
        async for schedule in await self._repository.all_():
            self._schedule_sequence += 1
            schedule_stops = []

            for stop in schedule.stops:
                self._schedule_stop_sequence += 1
                schedule_stops.append(
                    await self._generate_schedule_stop(
                        schedule_stops_f,
                        stop,
                    ),
                )

            export_schedule = schedules_pb2.Schedule(
                sequence=self._schedule_sequence,
                id=schedule.id,
                type=schedule.type,
                route=await self._get_route_stop(
                    schedule,
                    route_stops_f,
                ),
                schedule_stops=schedule_stops,
            )

            first_departure = int(
                schedule.stops[0].departure_at.ToDatetime().timestamp(),
            )

            await self._redis.list_(
                "routes.{0}.schedules".format(export_schedule.route),
            ).push(
                pickle.dumps(
                    (export_schedule.sequence, first_departure),
                ),
            )
            await protobuf.dump(export_schedule, schedules_f)

    async def _generate_route(
        self,
        schedule: models_pb2.Schedule,
        route_stops_f: binary.AsyncBufferedIOBase,
    ) -> int:
        self._route_sequence += 1
        route_stops = []

        for order, stop in enumerate(schedule.stops):
            self._route_stop_sequence += 1
            route_stop = schedules_pb2.RouteStop(
                sequence=self._route_stop_sequence,
                route=self._route_sequence,
                stop=await self._get_stop_sequence(stop.point),
                order=order,
            )

            await protobuf.dump(route_stop, route_stops_f)
            route_stops.append(route_stop)
            await self._redis.list_(
                "stops.{0}.route_stops".format(route_stop.stop),
            ).push(route_stop.sequence)

        route = schedules_pb2.Route(
            sequence=self._route_sequence,
            route_stops=[r_stop.sequence for r_stop in route_stops],
        )

        await self._routes.set_(str(route.sequence), route.SerializeToString())

        return route.sequence

    async def _get_route_stop(
        self,
        schedule: models_pb2.Schedule,
        route_stops_f: binary.AsyncBufferedIOBase,
    ) -> int:
        id_parts = [
            str(
                h3.geo_to_h3(
                    lat=stop.point.coordinates.latitude,
                    lng=stop.point.coordinates.longitude,
                    resolution=9,
                ),
            )
            for stop in schedule.stops
        ]

        identifier = hashlib.blake2b("\x00".join(id_parts).encode()).hexdigest()
        route_sequence = await self._route_sequences.get(identifier)

        if route_sequence:
            return int(route_sequence)

        route_sequence_int = await self._generate_route(schedule, route_stops_f)

        await self._route_sequences.set_(identifier, route_sequence_int)

        return route_sequence_int

    async def _get_stop_sequence(self, point: models_pb2.Point) -> int:
        identifier = str(
            h3.geo_to_h3(
                lat=point.coordinates.latitude,
                lng=point.coordinates.longitude,
                resolution=9,
            ),
        )

        stop_sequence = await self._stop_sequences.get(identifier)

        if stop_sequence:
            return int(stop_sequence)

        self._stop_sequence += 1
        stop = schedules_pb2.Stop(
            id=identifier,
            sequence=self._stop_sequence,
            transfer_time=_MIN_TRANSFER_TIME,
        )

        await self._stops.set_(str(stop.sequence), stop.SerializeToString())
        await self._stop_sequences.set_(stop.id, stop.sequence)

        return stop.sequence

    async def _store_routes(self, path: pathlib.Path) -> None:
        async with aiofiles.open(
            str(path.joinpath("routes.bin")),
            mode=_FILE_MODE,
        ) as routes_f:
            for sequence in range(self._route_sequence + 1):
                route = schedules_pb2.Route()
                route.ParseFromString((await self._routes.get(str(sequence))) or b"")

                schedules_sorted = sorted(
                    [
                        pickle.loads(pickled_schedule)  # nosec
                        async for pickled_schedule in self._redis.list_(
                            "routes.{0}.schedules".format(route.sequence),
                        ).to_iterable()
                    ],
                    key=lambda seg: seg[1],
                )

                route.schedules.extend([schedule[0] for schedule in schedules_sorted])

                await protobuf.dump(route, routes_f)

    async def _store_stops(self, path: pathlib.Path) -> None:
        async with aiofiles.open(
            str(path.joinpath("stops.bin")),
            mode=_FILE_MODE,
        ) as stops_f:
            for sequence in range(self._stop_sequence + 1):
                stop = schedules_pb2.Stop()
                stop.ParseFromString((await self._stops.get(str(sequence))) or b"")
                stop.route_stops.extend(
                    [
                        int(rs_sequence)
                        async for rs_sequence in self._redis.list_(
                            "stops.{0}.route_stops".format(stop.sequence),
                        ).to_iterable()
                    ],
                )

                schedule_stops = sorted(
                    [
                        pickle.loads(pickled_s_stop)  # nosec
                        async for pickled_s_stop in self._redis.list_(
                            "stops.{0}.schedule_stops".format(stop.sequence),
                        ).to_iterable()
                    ],
                    key=lambda seg: seg[1],
                )

                stop.schedule_stops.extend([s_stop[0] for s_stop in schedule_stops])

                await protobuf.dump(stop, stops_f)

    async def _generate_schedule_stop(
        self,
        schedule_stops_f: binary.AsyncBufferedIOBase,
        stop: models_pb2.Stop,
    ) -> int:
        schedule_stop = schedules_pb2.ScheduleStop(
            sequence=self._schedule_stop_sequence,
            schedule=self._schedule_sequence,
            stop=await self._get_stop_sequence(
                stop.point,
            ),
            departure_at=max(
                0,
                int(stop.departure_at.ToDatetime().timestamp()),
            ),
            arrival_at=max(
                0,
                int(stop.arrival_at.ToDatetime().timestamp()),
            ),
            order=stop.order,
        )

        await self._redis.list_(
            "stops.{0}.schedule_stops".format(
                schedule_stop.stop,
            ),
        ).push(
            pickle.dumps(
                (
                    schedule_stop.sequence,
                    schedule_stop.departure_at,
                ),
            ),
        )

        await protobuf.dump(schedule_stop, schedule_stops_f)

        return schedule_stop.sequence
