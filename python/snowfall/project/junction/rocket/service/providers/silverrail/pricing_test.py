from unittest import mock

from snowfall.project.junction.rocket.service.providers.silverrail import (
    pricing,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    amqp_pb2,
    models_pb2,
)


async def test_pricing_successful(  # noqa: WPS218
    silverrail_quote_task_consumer: pricing.QuoteTaskConsumer,
    silverrail_quote_result_producer: mock.AsyncMock,
) -> None:
    quote_id = "fake-id"
    offer_id = "offer-id"
    task = mock.Mock(
        body=amqp_pb2.QuoteTask(
            quote=models_pb2.Quote(id=quote_id, offer_ids=[offer_id]),
        ),
    )
    await silverrail_quote_task_consumer._process_message(task)  # noqa: SLF001
    silverrail_quote_result_producer.publish.assert_awaited()
    quote_task_result = silverrail_quote_result_producer.publish.call_args[0][0]

    assert quote_task_result.quote.id == quote_id
    assert quote_task_result.quote.pay_company_id == "fake-pay-company-id"
    assert quote_task_result.quote.total_price.currency_code == "EUR"
    assert quote_task_result.quote.total_price.units == 31
    assert quote_task_result.quote.offer_ids[0] == "offer-id"

    quoted_offer = quote_task_result.quote.quoted_offers[0]
    assert quoted_offer.offer_id == "offer-id"
    assert quoted_offer.price.currency_code == "EUR"
    assert quoted_offer.price.units == 31
    assert len(quoted_offer.price_breakdown) == 1

    price_breakdown = quoted_offer.price_breakdown[0]
    assert price_breakdown.price.units == 31
    assert price_breakdown.price.currency_code == "EUR"
    assert (
        price_breakdown.breakdown_type
        == models_pb2.PriceBreakdown.BREAKDOWN_TYPE_BASE_FARE
    )

    rule = quoted_offer.rules[0]
    assert rule.body
    assert rule.title == "Ticketing"
