from unittest import mock

from snowfall.project.junction.rocket.service.providers.direct_ferries import (
    cache,
    pricing,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    amqp_pb2,
)
from snowfall.stdlib.transport.amqp import types
from snowfall.vendor.direct_ferries.models import (
    passenger,
)


async def test_process_message(
    quote_task_consumer: pricing.QuoteTaskConsumer,
    mock_quote_message: types.Message[amqp_pb2.QuoteTask],
    mock_offer_details: cache.OfferDetails,
    mock_combined_passenger_requirements: passenger.RoutePassengerInfo,
) -> None:
    with (
        mock.patch.object(
            quote_task_consumer,
            "_get_combined_passenger_requirements",
            new_callable=mock.AsyncMock,
        ) as mock_passenger_req,
        mock.patch(
            "snowfall.stdlib.persistence.redis.repository.PydanticRepository.fetch",
        ) as mock_offer_cache,
        mock.patch.object(
            quote_task_consumer._quote_result_producer,  # noqa: SLF001
            "publish",
            new_callable=mock.AsyncMock,
        ) as mock_quote_result_producer,
    ):
        mock_passenger_req.return_value = mock_combined_passenger_requirements
        mock_offer_cache.return_value = mock_offer_details
        await quote_task_consumer._process_message(mock_quote_message)  # noqa: SLF001

        mock_quote_result_producer.assert_awaited_once()
