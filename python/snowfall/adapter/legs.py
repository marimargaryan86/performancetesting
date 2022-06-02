from __future__ import annotations

import abc
import dataclasses
from typing import Optional, Sequence

import grpc

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.schedules.v1alpha import schedules_pb2, schedules_pb2_grpc


class NotFoundError(Exception):
    """Raised when a leg is not found."""


class UnknownError(Exception):
    """Raised when an unhandled error occurs."""


@dataclasses.dataclass(frozen=True)
class LegsPage(object):
    legs: Sequence[models_pb2.Leg]
    next_page_token: str = ""

    @classmethod
    def from_proto(
        cls,
        grpc_legs: schedules_pb2.ListLegsResponse,
    ) -> LegsPage:
        return cls(
            legs=grpc_legs.legs,
            next_page_token=grpc_legs.next_page_token,
        )


class Client(abc.ABC):
    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.Leg:
        """Fetch a leg resource."""

    @abc.abstractmethod
    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> LegsPage:
        """Find legs by IDs."""


class DictClient(Client):
    def __init__(self, legs: Sequence[models_pb2.Leg]) -> None:
        self._legs = {leg.id: leg for leg in legs}

    async def get(self, leg_id: str) -> models_pb2.Leg:
        leg = self._legs.get(leg_id)

        if not leg:
            raise NotFoundError()

        return leg

    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> LegsPage:
        return LegsPage(legs=list(self._legs.values()))


class GrpcClient(Client):
    def __init__(
        self,
        schedules: schedules_pb2_grpc.ScheduleServiceStub,
        timeout: int = 10,
    ):
        self._schedules = schedules
        self._timeout = timeout

    async def get(self, leg_id: str) -> models_pb2.Leg:
        try:
            response = await self._schedules.GetLeg(
                schedules_pb2.GetLegRequest(id=leg_id),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Leg with ID '{id}' not found.".format(id=leg_id),
                ) from exc

            raise UnknownError() from exc

        return response.leg

    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> LegsPage:
        request = schedules_pb2.ListLegsRequest(
            ids=list(identifiers),
            page_token=cursor or "",
        )
        if limit is not None:
            request.page_size = limit

        try:
            response = await self._schedules.ListLegs(request, timeout=self._timeout)
        except grpc.aio.AioRpcError as exc:
            raise UnknownError() from exc

        return LegsPage(
            legs=list(response.legs),
            next_page_token=response.next_page_token,
        )
