from typing import Type
from unittest import mock

import grpc
import pytest

from snowfall import fixtures
from snowfall.project.junction.adapter import orders
from snowfall.project.junction.service.orders.v1alpha import (
    models_pb2,
    orders_pb2,
    orders_pb2_grpc,
)


class TestDictClient(object):
    async def test_single_order_is_retrievable(
        self,
        orders_client: orders.Client,
    ) -> None:
        order = await orders_client.get_order(fixtures.ORDERS[0])
        assert order.id == fixtures.ORDERS[0]

    async def test_missing_order_throws_error(
        self,
        orders_client: orders.Client,
    ) -> None:
        with pytest.raises(orders.NotFoundError):
            await orders_client.get_order(fixtures.NOT_FOUND)

    async def test_multiple_orders_are_retrievable(
        self,
        orders_client: orders.Client,
    ) -> None:
        found_orders = await orders_client.find_orders(
            identifiers=fixtures.ORDERS,
            limit=100,
        )
        assert len(found_orders.orders) == 2


class TestGrpcClient(object):
    @pytest.mark.parametrize(
        "error, expected",
        [
            (
                grpc.aio.AioRpcError(
                    code=grpc.StatusCode.NOT_FOUND,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                ),
                orders.NotFoundError,
            ),
            (
                grpc.aio.AioRpcError(
                    code=grpc.StatusCode.UNKNOWN,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                ),
                orders.UnknownError,
            ),
        ],
    )
    async def test_error_responses(
        self,
        error: grpc.aio.AioRpcError,
        expected: Type[Exception],
    ) -> None:
        stub = mock.create_autospec(orders_pb2_grpc.OrderServiceStub)
        stub.GetOrder = mock.AsyncMock(side_effect=error)
        client = orders.GrpcClient(stub)
        with pytest.raises(expected):
            await client.get_order(fixtures.NOT_FOUND)

    async def test_single_order_is_retrievable(self) -> None:
        proto = models_pb2.Order(id=fixtures.ORDERS[0])
        stub = mock.create_autospec(orders_pb2_grpc.OrderServiceStub)
        stub.GetOrder = mock.AsyncMock(
            return_value=orders_pb2.GetOrderResponse(order=proto),
        )
        client = orders.GrpcClient(stub)
        order = await client.get_order(fixtures.ORDERS[0])
        assert order.id == fixtures.ORDERS[0]
