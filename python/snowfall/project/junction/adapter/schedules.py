from __future__ import annotations

import abc
from typing import Optional, Sequence

import grpc

from snowfall.project.junction.adapter import errors
from snowfall.project.junction.service.schedules.v1alpha import (
    schedules_pb2,
    schedules_pb2_grpc,
)
from snowfall.stdlib.v1alpha import models_pb2


class NotFoundError(Exception):
    """Raised when a schedule is not found."""


class UnknownError(Exception):
    """Raised when an unhandled error occurs."""


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
    ) -> schedules_pb2.ListSchedulesResponse:
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
    ) -> schedules_pb2.ListSchedulesResponse:
        return schedules_pb2.ListSchedulesResponse(
            schedules=list(self._schedules.values()),
        )


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
    ) -> schedules_pb2.ListSchedulesResponse:
        request = schedules_pb2.ListSchedulesRequest(
            ids=list(identifiers),
            page_token=cursor or "",
        )
        if limit is not None:
            request.page_size = limit

        try:
            return await errors.handle_grpc_errors(
                self._schedules.ListSchedules(request, timeout=self._timeout),
            )
        except grpc.aio.AioRpcError as exc:
            raise UnknownError() from exc
