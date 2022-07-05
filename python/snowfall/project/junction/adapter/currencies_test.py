from typing import Type
from unittest import mock

import grpc
import pytest

from snowfall import fixtures
from snowfall.project.junction.adapter import currencies
from snowfall.project.junction.service.currencies.v1alpha import (
    currencies_pb2,
    currencies_pb2_grpc,
)


@pytest.mark.asyncio
class TestDictClient(object):
    async def test_conversion_is_retrievable(
        self,
        currencies_client: currencies.Client,
    ) -> None:
        from_currency = "USD"
        to_currency = "EUR"
        amount_before = 10
        expected_amount_after = 9
        amount_after = await currencies_client.convert(
            from_currency=from_currency,
            to_currency=to_currency,
            amount=amount_before,
        )
        assert amount_after == expected_amount_after


@pytest.mark.asyncio
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
                currencies.NotFoundError,
            ),
        ],
    )
    async def test_error_responses(
        self,
        error: grpc.aio.AioRpcError,
        expected: Type[Exception],
    ) -> None:
        stub = mock.create_autospec(currencies_pb2_grpc.CurrencyServiceStub)
        stub.Convert = mock.AsyncMock(side_effect=error)
        client = currencies.GrpcClient(stub)
        amount = 10
        with pytest.raises(expected):
            await client.convert(
                fixtures.NOT_FOUND,
                fixtures.NOT_FOUND,
                amount,
            )

    async def test_conversion_amount_is_retrievable(self) -> None:
        stub = mock.create_autospec(currencies_pb2_grpc.CurrencyServiceStub)
        stub.Convert = mock.AsyncMock(
            return_value=currencies_pb2.ConvertResponse(amount=95),
        )
        client = currencies.GrpcClient(stub)
        amount = await client.convert(
            fixtures.CURRENCIES[0],
            fixtures.CURRENCIES[1],
            100,
        )
        assert amount == 95
