from __future__ import annotations

import abc
import dataclasses
from typing import Optional, Sequence

import grpc

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.schedules.v1alpha import schedules_pb2, schedules_pb2_grpc


class NotFoundError(Exception):
    """Raised when a schedule is not found."""


class UnknownError(Exception):
    """Raised when an unhandled error occurs."""


@dataclasses.dataclass(frozen=True)
class SchedulesPage(object):
    schedules: Sequence[models_pb2.Schedule]
    next_page_token: Optional[str] = None

    @classmethod
    def from_proto(
        cls,
        grpc_schedules: schedules_pb2.ListSchedulesResponse,
    ) -> SchedulesPage:
        return cls(
            schedules=grpc_schedules.schedules,
            next_page_token=grpc_schedules.next_page_token,
        )


class Client(abc.ABC):
    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.Schedule:
        """Fetch a schedule resource."""

    @abc.abstractmethod
    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: int,
        cursor: Optional[str] = None,
    ) -> SchedulesPage:
        """Find schedules by IDs."""

    async def get_stop(self, identifier: str) -> models_pb2.Stop:
        """Fetch a stop resource."""

    async def get_next_stop(self, identifier: str) -> models_pb2.Stop:
        """Fetch the next stop resource from the previous stop id."""


class DictClient(Client):
    def __init__(self, schedules: Sequence[models_pb2.Schedule]) -> None:
        self._schedules = {schedule.id: schedule for schedule in schedules}

    async def get(self, schedule_id: str) -> models_pb2.Schedule:
        if schedule_id not in self._schedules:
            raise NotFoundError()

        return models_pb2.Schedule(id=schedule_id)

    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: int,
        cursor: Optional[str] = None,
    ) -> SchedulesPage:
        return SchedulesPage(schedules=list(self._schedules.values()))

    async def get_stop(self, stop_id: str) -> models_pb2.Stop:
        stops = [
            stop.id for schedule in self._schedules.values() for stop in schedule.stops
        ]
        if stop_id not in stops:
            raise NotFoundError()

        return models_pb2.Stop(id=stop_id)

    async def get_next_stop(self, stop_id: str) -> models_pb2.Stop:
        for schedule in self._schedules.values():
            for index, stop in enumerate(schedule.stops):
                if stop.id == stop_id and index < len(schedule.stops) - 1:
                    return models_pb2.Stop(id=schedule.stops[index + 1].id)

        raise NotFoundError()


class GrpcClient(Client):
    def __init__(self, schedules: schedules_pb2_grpc.ScheduleServiceStub):
        self._schedules = schedules

    async def get(self, schedule_id: str) -> models_pb2.Schedule:
        try:
            response = await self._schedules.GetSchedule(
                schedules_pb2.GetScheduleRequest(id=schedule_id),
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Schedule with ID '{id}' not found.".format(id=schedule_id),
                ) from exc

            raise UnknownError() from exc

        return response.schedule

    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: int,
        cursor: Optional[str] = None,
    ) -> SchedulesPage:
        try:
            response = await self._schedules.ListSchedules(
                schedules_pb2.ListSchedulesRequest(
                    ids=list(identifiers),
                    page_size=limit,
                    page_token=cursor or "",
                ),
            )
        except grpc.aio.AioRpcError as exc:
            raise UnknownError() from exc

        return SchedulesPage(
            schedules=list(response.schedules),
            next_page_token=response.next_page_token,
        )

    async def get_stop(self, stop_id: str) -> models_pb2.Stop:
        try:
            response = await self._schedules.GetStop(
                schedules_pb2.GetNextStopRequest(id=stop_id),
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Stop with ID '{id}' not found.".format(id=stop_id),
                ) from exc

            raise UnknownError() from exc

        return response.stop

    async def get_next_stop(self, stop_id: str) -> models_pb2.Stop:
        try:
            response = await self._schedules.GetNextStop(
                schedules_pb2.GetNextStopRequest(id=stop_id),
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "No Stop after stop with ID '{id}' found.".format(id=stop_id),
                ) from exc

            raise UnknownError() from exc

        return response.stop
