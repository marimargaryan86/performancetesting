from collections.abc import Sequence
from unittest import mock

import grpc

from snowfall.project.junction.rocket.service.searches import amqp
from snowfall.project.junction.rocket.service.searches import grpc as searches_grpc
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    amqp_pb2,
    grpc_pb2,
    models_pb2,
)
from snowfall.stdlib.transport.grpc import testing

_QUOTES = ("80743d96-5543-45da-a4e0-18dff6a5be98",)
_OFFERS = ("929b8b1b-5f83-4412-a615-097ae8b1f6fb",)
_RESELLER_ID = "9ccfd536-6aa0-4b9b-a564-679de7e37835"
_RESELLER_PAY_COMPANY_ID = "5331d442-88d2-4c4a-85c3-b652a48f853b"
_RESELLER_CURRENCY = "EUR"


class MockIteratorWithCursor:
    def __init__(self, offers: Sequence[models_pb2.Offer]):
        self.iter = iter(offers)
        self.limit_calls: list[int] = []

    def __aiter__(self):  # type: ignore[no-untyped-def]  # noqa: ANN204
        return self

    async def __anext__(self):  # type: ignore[no-untyped-def]  # noqa: ANN204
        try:
            return next(self.iter)
        except StopIteration as err:
            raise StopAsyncIteration from err

    async def cursor(self) -> str:
        return "next-page-token"

    def limit(self, limit: int) -> None:
        self.limit_calls.append(limit)


class TestQuotes:
    async def test_quote_task_published(
        self,
        producer_obj: mock.AsyncMock,
        grpc_context: grpc.aio.ServicerContext,
    ) -> None:
        offers = [models_pb2.Offer(id=_OFFERS[0], rail=models_pb2.RailOffer())]
        mock_repository = mock.AsyncMock()
        mock_repository.create.return_value = models_pb2.Quote(id=_QUOTES[0])
        mock_repository.find.return_value = MockIteratorWithCursor(offers=offers)

        quotes_service = searches_grpc.QuoteService(
            quotes_repo=mock_repository,
            offers_repo=mock_repository,
            publisher=amqp.QuoteTaskProducer(
                producer=producer_obj,
                routing_key="quotes.offers",
            ),
        )

        quotes_response = await quotes_service.CreateQuote(
            request=grpc_pb2.CreateQuoteRequest(
                offer_ids=list(_OFFERS),
                reseller_id=_RESELLER_ID,
                reseller_pay_company_id=_RESELLER_PAY_COMPANY_ID,
                reseller_currency=_RESELLER_CURRENCY,
            ),
            context=grpc_context,
        )

        producer_obj.publish.assert_called_once_with(
            amqp_pb2.QuoteTask(
                quote=quotes_response.quote,
                reseller_id=_RESELLER_ID,
            ),
            "quotes.offers",
        )

        assert quotes_response.quote.id == _QUOTES[0]

    async def test_create_quote_offers_not_found(
        self,
        producer_obj: mock.AsyncMock,
        grpc_context: grpc.aio.ServicerContext,
    ) -> None:
        mock_repository = mock.AsyncMock()
        mock_repository.find.return_value = MockIteratorWithCursor(offers=[])

        quotes_service = searches_grpc.QuoteService(
            quotes_repo=mock_repository,
            offers_repo=mock_repository,
            publisher=amqp.QuoteTaskProducer(
                producer=producer_obj,
                routing_key="quotes.offers",
            ),
        )
        with testing.assert_aborted(grpc.StatusCode.NOT_FOUND):
            await quotes_service.CreateQuote(
                request=grpc_pb2.CreateQuoteRequest(
                    offer_ids=list(_OFFERS),
                    reseller_id=_RESELLER_ID,
                    reseller_pay_company_id=_RESELLER_PAY_COMPANY_ID,
                    reseller_currency=_RESELLER_CURRENCY,
                ),
                context=grpc_context,
            )

        mock_repository.find.assert_called_once_with(ids=list(_OFFERS), cursor="")

    async def test_create_quote_one_offer_not_found(
        self,
        producer_obj: mock.AsyncMock,
        grpc_context: grpc.aio.ServicerContext,
    ) -> None:
        offers = [
            models_pb2.Offer(id=_OFFERS[0], car_rental=models_pb2.CarRentalOffer()),
        ]
        not_found_offer = "32c23ab6-1044-49e4-9e7a-0d44f1728e6e"
        request_offer_ids = [_OFFERS[0], not_found_offer]
        mock_repository = mock.AsyncMock()
        mock_repository.find.return_value = MockIteratorWithCursor(offers=offers)

        quotes_service = searches_grpc.QuoteService(
            quotes_repo=mock_repository,
            offers_repo=mock_repository,
            publisher=amqp.QuoteTaskProducer(
                producer=producer_obj,
                routing_key="quotes.offers",
            ),
        )
        with testing.assert_aborted(grpc.StatusCode.NOT_FOUND):
            await quotes_service.CreateQuote(
                request=grpc_pb2.CreateQuoteRequest(
                    offer_ids=request_offer_ids,
                    reseller_id=_RESELLER_ID,
                    reseller_pay_company_id=_RESELLER_PAY_COMPANY_ID,
                    reseller_currency=_RESELLER_CURRENCY,
                ),
                context=grpc_context,
            )

        mock_repository.find.assert_called_once_with(ids=request_offer_ids, cursor="")

    async def test_create_quote_invalid_verticals_found(
        self,
        producer_obj: mock.AsyncMock,
        grpc_context: grpc.aio.ServicerContext,
    ) -> None:
        offers = [models_pb2.Offer(id=_OFFERS[0])]
        mock_repository = mock.AsyncMock()
        mock_repository.find.return_value = MockIteratorWithCursor(offers=offers)

        quotes_service = searches_grpc.QuoteService(
            quotes_repo=mock_repository,
            offers_repo=mock_repository,
            publisher=amqp.QuoteTaskProducer(
                producer=producer_obj,
                routing_key="quotes.offers",
            ),
        )
        with testing.assert_aborted(grpc.StatusCode.FAILED_PRECONDITION):
            await quotes_service.CreateQuote(
                request=grpc_pb2.CreateQuoteRequest(
                    offer_ids=list(_OFFERS),
                    reseller_id=_RESELLER_ID,
                    reseller_pay_company_id=_RESELLER_PAY_COMPANY_ID,
                    reseller_currency=_RESELLER_CURRENCY,
                ),
                context=grpc_context,
            )

        mock_repository.find.assert_called_once_with(ids=list(_OFFERS), cursor="")

    async def test_create_quote_vertical_mismatch_found(
        self,
        producer_obj: mock.AsyncMock,
        grpc_context: grpc.aio.ServicerContext,
    ) -> None:
        request_offer_ids = [_OFFERS[0], "cfd84cd9-f712-437a-ad8e-5b1c86e2b5f7"]
        offers = [
            models_pb2.Offer(id=request_offer_ids[0], rail=models_pb2.RailOffer()),
            models_pb2.Offer(id=request_offer_ids[1], ferry=models_pb2.FerryOffer()),
        ]
        mock_repository = mock.AsyncMock()
        mock_repository.find.return_value = MockIteratorWithCursor(offers=offers)

        quotes_service = searches_grpc.QuoteService(
            quotes_repo=mock_repository,
            offers_repo=mock_repository,
            publisher=amqp.QuoteTaskProducer(
                producer=producer_obj,
                routing_key="quotes.offers",
            ),
        )
        with testing.assert_aborted(grpc.StatusCode.FAILED_PRECONDITION):
            await quotes_service.CreateQuote(
                request=grpc_pb2.CreateQuoteRequest(
                    offer_ids=request_offer_ids,
                    reseller_id=_RESELLER_ID,
                    reseller_pay_company_id=_RESELLER_PAY_COMPANY_ID,
                    reseller_currency=_RESELLER_CURRENCY,
                ),
                context=grpc_context,
            )

        mock_repository.find.assert_called_once_with(ids=request_offer_ids, cursor="")

    async def test_quote_is_retrievable(
        self,
        producer_obj: mock.AsyncMock,
        grpc_context: grpc.aio.ServicerContext,
    ) -> None:
        quote = models_pb2.Quote(id=_QUOTES[0])
        mock_repository = mock.AsyncMock()
        mock_repository.find_by_id.return_value = quote

        quotes_service = searches_grpc.QuoteService(
            quotes_repo=mock_repository,
            offers_repo=mock_repository,
            publisher=amqp.QuoteTaskProducer(
                producer=producer_obj,
                routing_key="quotes.offers",
            ),
        )

        quote_response = await quotes_service.GetQuote(
            request=grpc_pb2.GetQuoteRequest(id=_QUOTES[0]),
            context=grpc_context,
        )

        assert quote_response.quote == quote
        mock_repository.find_by_id.assert_called_once_with(_QUOTES[0])

    async def test_quote_not_found(
        self,
        producer_obj: mock.AsyncMock,
        grpc_context: grpc.aio.ServicerContext,
    ) -> None:
        mock_repository = mock.AsyncMock()
        mock_repository.find_by_id.return_value = None

        quotes_service = searches_grpc.QuoteService(
            quotes_repo=mock_repository,
            offers_repo=mock_repository,
            publisher=amqp.QuoteTaskProducer(
                producer=producer_obj,
                routing_key="quotes.offers",
            ),
        )

        with testing.assert_aborted(grpc.StatusCode.NOT_FOUND):
            await quotes_service.GetQuote(
                request=grpc_pb2.GetQuoteRequest(id=_QUOTES[0]),
                context=grpc_context,
            )

        mock_repository.find_by_id.assert_called_once_with(_QUOTES[0])
