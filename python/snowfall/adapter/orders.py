from __future__ import annotations

import abc
import dataclasses
import uuid
from typing import Optional, Sequence

import grpc

from snowfall.junction.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.junction.orders.v1alpha import models_pb2, orders_pb2, orders_pb2_grpc


class NotFoundError(Exception):
    """Raised when a order is not found."""


class UnknownError(Exception):
    """Raised when an unhandled error occurs."""


@dataclasses.dataclass(frozen=True)
class OrdersPage(object):
    orders: Sequence[models_pb2.Order]
    next_page_token: Optional[str] = None

    @classmethod
    async def from_proto(cls, grpc_orders: orders_pb2.ListOrdersResponse) -> OrdersPage:
        return cls(
            orders=grpc_orders.orders,
            next_page_token=grpc_orders.next_page_token,
        )


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(self, offers: Sequence[offers_pb2.Offer]) -> models_pb2.Order:
        """Create a new order resource."""

    @abc.abstractmethod
    async def find(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> OrdersPage:
        """Fetch all order resources."""

    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.Order:
        """Fetch a order resource."""

    @abc.abstractmethod
    async def add_offers(
        self,
        order_id: str,
        offers: Sequence[offers_pb2.Offer],
    ) -> models_pb2.Order:
        """Add offers to an order resource."""


class DictClient(Client):
    def __init__(self, orders: Sequence[models_pb2.Order]) -> None:
        self._orders = {order.id: order for order in orders}

    async def create(self, offers: Sequence[offers_pb2.Offer]) -> models_pb2.Order:
        order = models_pb2.Order(
            id=str(uuid.uuid4()),
            offers=offers,
        )
        self._orders[order.id] = order

        return order

    async def find(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> OrdersPage:
        return OrdersPage(orders=list(self._orders.values()))

    async def get(self, order_id: str) -> models_pb2.Order:
        if order_id not in self._orders:
            raise NotFoundError()

        return self._orders[order_id]

    async def add_offers(
        self,
        order_id: str,
        offers: Sequence[offers_pb2.Offer],
    ) -> models_pb2.Order:
        if order_id not in self._orders:
            raise NotFoundError()

        self._orders[order_id].offers.extend(offers)

        return self._orders[order_id]


class GrpcClient(Client):
    def __init__(self, orders: orders_pb2_grpc.OrderServiceStub, timeout: int = 10):
        self._orders = orders
        self._timeout = timeout

    async def create(self, offers: Sequence[offers_pb2.Offer]) -> models_pb2.Order:
        try:
            response = await self._orders.EnqueueOrder(
                orders_pb2.EnqueueOrderRequest(
                    offers=offers,
                ),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            raise UnknownError(exc.details()) from exc

        return response.order

    async def find(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> OrdersPage:
        # TODO: handle INVALID_ARGUMENT
        request = orders_pb2.ListOrdersRequest(
            page_token=cursor or "",
        )
        if limit is not None:
            request.page_size = limit

        response = await self._orders.ListOrders(request, timeout=self._timeout)

        return await OrdersPage.from_proto(response)

    async def get(self, order_id: str) -> models_pb2.Order:
        try:
            response = await self._orders.GetOrder(
                orders_pb2.GetOrderRequest(id=order_id),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Order with ID '{id}' not found.".format(id=order_id),
                ) from exc

            raise UnknownError() from exc

        return response.order

    async def add_offers(
        self,
        order_id: str,
        offers: Sequence[offers_pb2.Offer],
    ) -> models_pb2.Order:
        try:
            response = await self._orders.AddOffersToOrder(
                orders_pb2.AddOffersToOrderRequest(
                    offers=offers,
                ),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            raise UnknownError(exc.details()) from exc

        return response.order
