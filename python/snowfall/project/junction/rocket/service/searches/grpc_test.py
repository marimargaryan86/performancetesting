from unittest import mock

from snowfall.project.junction.rocket.service.searches import grpc, repository
from snowfall.project.junction.rocket.service.searches.v1alpha import amqp_pb2, grpc_pb2
from snowfall.stdlib.transport.grpc import testing


async def test_search_task_published(
    quote_service_tester: testing.ServerTester,
    producer_obj: mock.AsyncMock,
) -> None:
    response = await quote_service_tester.invoke_unary_unary(
        method=grpc.QuoteService.CreateQuote,
        request=grpc_pb2.CreateQuoteRequest(
            offer_id="",
            reseller_id="",
        ),
    )

    producer_obj.publish.assert_called_once_with(
        amqp_pb2.QuoteTask(
            quote=response.message.quote,
            reseller_id="",
        ),
        "quotes.offers",
    )


async def test_search_task_persisted(
    quote_service_tester: testing.ServerTester,
    quote_repository: repository.QuoteRepository,
) -> None:
    response = await quote_service_tester.invoke_unary_unary(
        method=grpc.QuoteService.CreateQuote,
        request=grpc_pb2.CreateQuoteRequest(
            offer_id="",
            reseller_id="",
        ),
    )

    persisted = await quote_repository.find_by_id(
        response.message.quote.id,
    )

    assert persisted is not None

    assert persisted.id == response.message.quote.id


async def test_quote_is_retrievable(
    quote_service_tester: testing.ServerTester,
) -> None:
    create_response = await quote_service_tester.invoke_unary_unary(
        method=grpc.QuoteService.CreateQuote,
        request=grpc_pb2.CreateQuoteRequest(
            offer_id="",
            reseller_id="",
        ),
    )

    retrieve_response = await quote_service_tester.invoke_unary_unary(
        method=grpc.QuoteService.GetQuote,
        request=grpc_pb2.GetQuoteRequest(
            id=create_response.message.quote.id,
        ),
    )

    assert retrieve_response.message.quote is not None
