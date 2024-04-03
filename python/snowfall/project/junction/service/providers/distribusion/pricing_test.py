from __future__ import annotations

from unittest import mock

from snowfall.project.junction.go.service.offers.v1 import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.service.providers.distribusion import pricing
from snowfall.stdlib.transport.amqp import types
from snowfall.vendor.distribusion import conftest
from snowfall.vendor.distribusion.models import connections


class TestPriceQuoteConsumer:
    async def test_process_message(
        self,
        price_quote_consumer: pricing.PriceQuoteConsumer,
        message: types.Message[offers_amqp_pb2.TripPriceQuoteTask],
    ) -> None:
        vacancy_response = await conftest.load_file_fixture("vacancy_response.json")

        offer = connections.ConnectionVacancy(
            identifier=vacancy_response["data"]["id"],
            total_price=vacancy_response["data"]["attributes"]["total_price"],
            vacant=vacancy_response["data"]["attributes"]["vacant"],
            fees=vacancy_response["data"]["relationships"]["fees"]["data"],
            currency=vacancy_response["meta"]["currency"],
        )

        price_quote_consumer._producer.publish = (  # type: ignore[method-assign] # noqa: SLF001
            mock.AsyncMock()
        )

        with mock.patch(
            "snowfall.project.junction.service.providers.distribusion.pricing.PriceQuoteConsumer._vacancy",
            return_value=offer,
        ):
            await price_quote_consumer._process_message(message)  # noqa: SLF001
            price_quote_consumer._producer.publish.assert_awaited_once()  # noqa: SLF001
