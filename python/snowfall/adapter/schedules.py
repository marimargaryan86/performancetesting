from __future__ import annotations

import abc
from typing import Sequence

import grpc

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.schedules.v1alpha import schedules_pb2, schedules_pb2_grpc


class NotFoundError(Exception):
    """Raised when a schedule is not found."""


class UnknownError(Exception):
    """Raised when an unhandled error occurs."""


class Client(abc.ABC):
    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.Schedule:
        """Fetch a schedule resource."""


class DictClient(Client):
    def __init__(self, schedules: Sequence[models_pb2.Schedule]) -> None:
        self._schedules = {schedule.id: schedule for schedule in schedules}

    async def get(self, schedule_id: str) -> models_pb2.Schedule:
        if schedule_id not in self._schedules:
            raise NotFoundError()

        return models_pb2.Schedule(id=schedule_id)


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
