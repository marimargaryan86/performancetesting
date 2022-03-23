from __future__ import annotations

import abc
import uuid
from typing import Sequence

import grpc

from snowfall.junction.orders.v1alpha import orders_pb2, orders_pb2_grpc


class NotFoundError(Exception):
    """Raised when a order is not found."""


class UnknownError(Exception):
    """Raised when an unhandled error occurs."""


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(self, request: orders_pb2.Order) -> orders_pb2.Order:
        """Create a new order resource."""

    async def get(self, identifier: str) -> orders_pb2.Order:
        """Fetch a order resource."""


class DictClient(Client):
    def __init__(self, orders: Sequence[orders_pb2.Order]) -> None:
        self._orders = {order.id: order for order in orders}

    async def create(self, request: orders_pb2.Order) -> orders_pb2.Order:
        order = orders_pb2.Order(
            id=str(uuid.uuid4()),
        )
        self._orders[order.id] = order

        return order

    async def get(self, order_id: str) -> orders_pb2.Order:
        if order_id not in self._orders:
            raise NotFoundError()

        return orders_pb2.Order(id=order_id)


class GrpcClient(Client):
    def __init__(self, orders: orders_pb2_grpc.OrderServiceStub):
        self._orders = orders

    async def create(self, order: orders_pb2.Order) -> orders_pb2.Order:
        try:
            response = await self._orders.EnqueueOrder(
                orders_pb2.EnqueueOrderRequest(order=order),
            )
        except grpc.aio.AioRpcError as exc:
            raise UnknownError(exc.details()) from exc

        return response.order

    async def get(self, order_id: str) -> orders_pb2.Order:
        try:
            response = await self._orders.GetOrder(
                orders_pb2.GetOrderRequest(id=order_id),
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Order with ID '{id}' not found.".format(id=order_id),
                ) from exc

            raise UnknownError() from exc

        return response.order
