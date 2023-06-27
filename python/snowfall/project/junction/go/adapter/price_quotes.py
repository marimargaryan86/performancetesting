import abc
import datetime
from collections.abc import Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.junction.go.service.offers.v1 import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(  # noqa: WPS211
        self,
        offer_id: str,
        option_ids: Sequence[str],
        session_token: str,
        pay_company_id: str,
        reseller_id: str,
    ) -> models_pb2.PriceQuoteContainer:
        """Create a price quote."""

    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.PriceQuoteContainer:
        """Get a price quote."""


class DictClient(Client):
    def __init__(self, price_quotes: Sequence[models_pb2.PriceQuoteContainer]) -> None:
        self._searches: dict[str, models_pb2.PriceQuoteContainer] = {
            price_quote.id: price_quote for price_quote in price_quotes
        }

    async def create(  # noqa: WPS211
        self,
        offer_id: str,
        option_ids: Sequence[str],
        session_token: str,
        pay_company_id: str,
        reseller_id: str,
    ) -> models_pb2.PriceQuoteContainer:
        expires_at = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
            days=1,
        )
        price_breakdown = [
            models_pb2.PriceBreakdown(
                price=money.from_string("3.37", money.Currency("EUR")).protobuf(),
                breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FEE,
            ),
            models_pb2.PriceBreakdown(
                price=money.from_string("10.00", money.Currency("EUR")).protobuf(),
                breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_TAX,
            ),
        ]
        price_quote = models_pb2.PriceQuoteContainer(
            id=string.uuid(),
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            quotes=[
                models_pb2.PriceQuote(
                    id=string.uuid(),
                    expires_at=protobuf.datetime_to_protobuf(expires_at),
                    price=money.from_string("13.37", money.Currency("EUR")).protobuf(),
                    price_breakdown=price_breakdown,
                )
                for _ in option_ids
            ],
            offer_id=offer_id,
            option_ids=option_ids,
            session_token=session_token,
        )
        self._searches[price_quote.id] = price_quote

        return price_quote

    async def get(self, identifier: str) -> models_pb2.PriceQuoteContainer:
        try:
            return self._searches[identifier]
        except KeyError as err:
            raise errors.NotFoundError() from err


class GrpcClient(Client):
    def __init__(
        self,
        price_quotes: grpc_pb2_grpc.PriceQuoteServiceStub,
        timeout: int = 10,
    ):
        self._price_quotes = price_quotes
        self._timeout = timeout

    async def create(  # noqa: WPS211
        self,
        offer_id: str,
        option_ids: Sequence[str],
        session_token: str,
        pay_company_id: str,
        reseller_id: str,
    ) -> models_pb2.PriceQuoteContainer:
        response = await errors.handle_grpc_errors(
            self._price_quotes.CreatePriceQuote(
                grpc_pb2.CreatePriceQuoteRequest(
                    offer_id=offer_id,
                    option_ids=option_ids,
                    session_token=session_token,
                    pay_company_id=pay_company_id,
                    reseller_id=reseller_id,
                ),
                timeout=self._timeout,
            ),
        )

        return response.price_quote

    async def get(self, identifier: str) -> models_pb2.PriceQuoteContainer:
        response = await errors.handle_grpc_errors(
            self._price_quotes.GetPriceQuote(
                grpc_pb2.GetPriceQuoteRequest(id=identifier),
                timeout=self._timeout,
            ),
        )

        return response.price_quote
