from unittest import mock

from snowfall import fixtures
from snowfall.project.pay.adapter import currencies
from snowfall.project.pay.service.currencies.v1alpha import (
    currencies_pb2,
    currencies_pb2_grpc,
)
from snowfall.stdlib.money import Currency


class TestDictClient(object):
    async def test_conversion_is_retrievable(
        self,
        currencies_client: currencies.Client,
    ) -> None:
        from_currency = Currency("USD")
        to_currency = Currency("EUR")
        amount_before = 10
        expected_amount_after = 9
        conversion = await currencies_client.convert(
            from_currency=from_currency,
            to_currency=to_currency,
            amount=amount_before,
        )
        assert conversion.amount == expected_amount_after


class TestGrpcClient(object):
    async def test_conversion_amount_is_retrievable(self) -> None:
        stub = mock.create_autospec(currencies_pb2_grpc.CurrencyServiceStub)
        stub.Convert = mock.AsyncMock(
            return_value=currencies_pb2.ConvertResponse(amount=95),
        )
        client = currencies.GrpcClient(stub)
        conversion = await client.convert(
            fixtures.CURRENCIES[0],
            fixtures.CURRENCIES[1],
            100,
        )
        assert conversion.amount == 95
