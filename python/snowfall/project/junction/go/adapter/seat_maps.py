from __future__ import annotations

import abc
import asyncio
from typing import Sequence

from snowfall.project.junction.go.v1alpha import seat_maps_pb2
from snowfall.stdlib.transport.amqp import rpc_client


class Client(abc.ABC):
    @abc.abstractmethod
    async def get_seat_map(
        self,
        identifier: str,
    ) -> seat_maps_pb2.SeatMapResult:
        """Find seat maps by IDs."""


class DictClient(Client):
    def __init__(
        self,
        seat_maps: Sequence[seat_maps_pb2.SeatMapResult],
    ):
        self._seat_maps = seat_maps

    async def get_seat_map(
        self,
        identifier: str,
    ) -> seat_maps_pb2.SeatMapResult:
        return self._seat_maps[0]


class RpcClient(Client):
    def __init__(
        self,
        client: rpc_client.RpcClient[seat_maps_pb2.SeatMapResult],
    ):
        self._client = client

    async def get_seat_map(
        self,
        offer_option_id: str,
    ) -> seat_maps_pb2.SeatMapResult:
        request = seat_maps_pb2.GetSeatMapTask(
            offer_option_id=offer_option_id,
        )
        try:
            return await self._client.call(request)
        except asyncio.TimeoutError:
            return seat_maps_pb2.SeatMapResult()
