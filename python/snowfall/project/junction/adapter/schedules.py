from __future__ import annotations

import abc
import dataclasses
from typing import Optional, Sequence

import grpc

from snowfall.project.junction.service.schedules.v1alpha import (
    schedules_pb2,
    schedules_pb2_grpc,
)
from snowfall.stdlib.v1alpha import models_pb2


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
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SchedulesPage:
        """Find schedules by IDs."""


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
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SchedulesPage:
        return SchedulesPage(schedules=list(self._schedules.values()))


class GrpcClient(Client):
    def __init__(
        self,
        schedules: schedules_pb2_grpc.ScheduleServiceStub,
        timeout: int = 10,
    ):
        self._schedules = schedules
        self._timeout = timeout

    async def get(self, schedule_id: str) -> models_pb2.Schedule:
        try:
            response = await self._schedules.GetSchedule(
                schedules_pb2.GetScheduleRequest(id=schedule_id),
                timeout=self._timeout,
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
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SchedulesPage:
        request = schedules_pb2.ListSchedulesRequest(
            ids=list(identifiers),
            page_token=cursor or "",
        )
        if limit is not None:
            request.page_size = limit

        try:
            response = await self._schedules.ListSchedules(
                request,
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            raise UnknownError() from exc

        return SchedulesPage(
            schedules=list(response.schedules),
            next_page_token=response.next_page_token,
        )
