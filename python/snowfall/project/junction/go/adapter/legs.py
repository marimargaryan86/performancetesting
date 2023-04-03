from __future__ import annotations

import abc
from typing import Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.junction.go.service.schedules.v1alpha import (
    schedules_pb2,
    schedules_pb2_grpc,
)
from snowfall.stdlib.v1alpha import models_pb2


class Client(abc.ABC):
    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.Leg:
        """Fetch a leg resource."""

    @abc.abstractmethod
    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: int | None = None,
        cursor: str | None = None,
    ) -> schedules_pb2.ListLegsResponse:
        """Find legs by IDs."""


class DictClient(Client):
    def __init__(self, legs: Sequence[models_pb2.Leg]) -> None:
        self._legs = {leg.id: leg for leg in legs}

    async def get(self, leg_id: str) -> models_pb2.Leg:
        leg = self._legs.get(leg_id)

        if not leg:
            raise errors.NotFoundError()

        return leg

    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: int | None = None,
        cursor: str | None = None,
    ) -> schedules_pb2.ListLegsResponse:
        return schedules_pb2.ListLegsResponse(legs=list(self._legs.values()))


class GrpcClient(Client):
    def __init__(
        self,
        schedules: schedules_pb2_grpc.ScheduleServiceStub,
        timeout: int = 10,
    ):
        self._schedules = schedules
        self._timeout = timeout

    async def get(self, leg_id: str) -> models_pb2.Leg:
        response = await errors.handle_grpc_errors(
            self._schedules.GetLeg(
                schedules_pb2.GetLegRequest(id=leg_id),
                timeout=self._timeout,
            ),
        )

        return response.leg

    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: int | None = None,
        cursor: str | None = None,
    ) -> schedules_pb2.ListLegsResponse:
        request = schedules_pb2.ListLegsRequest(
            ids=list(identifiers),
            page_token=cursor or "",
        )
        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._schedules.ListLegs(request, timeout=self._timeout),
        )
