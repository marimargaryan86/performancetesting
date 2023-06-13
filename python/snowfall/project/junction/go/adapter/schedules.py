from __future__ import annotations

import abc
from collections.abc import Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.junction.go.service.schedules.v1alpha import (
    schedules_pb2,
    schedules_pb2_grpc,
)
from snowfall.project.junction.go.v1alpha import models_pb2


class Client(abc.ABC):
    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.Schedule:
        """Fetch a schedule resource."""

    @abc.abstractmethod
    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: int | None = None,
        cursor: str | None = None,
    ) -> schedules_pb2.ListSchedulesResponse:
        """Find schedules by IDs."""


class DictClient(Client):
    def __init__(self, schedules: Sequence[models_pb2.Schedule]) -> None:
        self._schedules = {schedule.id: schedule for schedule in schedules}

    async def get(self, schedule_id: str) -> models_pb2.Schedule:
        if schedule_id not in self._schedules:
            raise errors.NotFoundError()

        return models_pb2.Schedule(id=schedule_id)

    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: int | None = None,
        cursor: str | None = None,
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
        response = await errors.handle_grpc_errors(
            self._schedules.GetSchedule(
                schedules_pb2.GetScheduleRequest(id=schedule_id),
                timeout=self._timeout,
            ),
        )

        return response.schedule

    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: int | None = None,
        cursor: str | None = None,
    ) -> schedules_pb2.ListSchedulesResponse:
        request = schedules_pb2.ListSchedulesRequest(
            ids=list(identifiers),
            page_token=cursor or "",
        )
        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._schedules.ListSchedules(request, timeout=self._timeout),
        )
