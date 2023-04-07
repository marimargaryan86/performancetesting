import uuid

from snowfall.project.junction.go.service.offers.pay_quotes_models import (
    PayQuoteResponse,
)
from snowfall.project.junction.go.service.offers.v1alpha.amqp_pb2 import (
    TripOfferSearchResult,
    TripPriceQuoteResult,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.v1alpha.money_pb2 import Money
from snowfall.vendor.junction.pay.client import Client as PayClient


class SkippedOfferError(Exception):
    """Raised when an offer is skipped."""


class PayQuotes(object):
    def __init__(
        self,
        pay_client: PayClient,
    ):
        self._pay_client = pay_client

    async def get_offer_search_quotes(
        self,
        search_result: TripOfferSearchResult,
        session_token: str,
        payer_id: str,
        to_currency: str,
    ) -> TripOfferSearchResult:
        for offer in search_result.offer.offers:
            offer_money = money.from_protobuf(offer.price)
            quote = await self._get_quote(
                amount=offer_money.amount,
                payer_id=payer_id,
                beneficiary_id=search_result.provider_company_id,
                from_currency=offer_money.currency.code,
                to_currency=to_currency,
            )
            offer.price.CopyFrom(
                Money(
                    currency_code=quote.data.relationships.to_currency.data.id,  # noqa:WPS219
                    units=quote.data.attributes.amount,
                    nanos=0,
                ),
            )
            offer.id = string.to_uuid(session_token, uuid.UUID(offer.id))
        search_result.offer.id = string.to_uuid(
            session_token,
            uuid.UUID(search_result.offer.id),
        )
        return search_result

    async def get_price_quote_quotes(
        self,
        search_result: TripPriceQuoteResult,
        session_token: str,
        payer_id: str,
        to_currency: str,
    ) -> TripPriceQuoteResult:
        price_quote_money = money.from_protobuf(search_result.price_quote.price)

        quote = await self._get_quote(
            amount=price_quote_money.amount,
            payer_id=payer_id,
            beneficiary_id=search_result.provider_company_id,
            from_currency=price_quote_money.currency.code,
            to_currency=to_currency,
        )

        search_result.price_quote.pay_quote_id = quote.data.id

        search_result.price_quote.price.CopyFrom(
            Money(
                currency_code=quote.data.relationships.to_currency.data.id,  # noqa:WPS219
                units=quote.data.attributes.amount,
                nanos=0,
            ),
        )

        search_result.price_quote.id = string.to_uuid(
            session_token,
            uuid.UUID(search_result.price_quote.id),
        )

        return search_result

    async def _get_quote(  # noqa: WPS211
        self,
        amount: int,
        payer_id: str,
        beneficiary_id: str,
        from_currency: str,
        to_currency: str,
    ) -> PayQuoteResponse:
        resp = await self._pay_client.create_quote(
            amount=amount,
            external_reference="",
            payer_id=payer_id,
            beneficiary_id=beneficiary_id,
            from_currency=from_currency,
            to_currency=to_currency,
        )
        return PayQuoteResponse(**resp)


class PayQuoteFetcher(object):
    def __init__(
        self,
        use_pay_for_currency_conversions: bool,
        pay_client: PayClient,
        payer_id: str,
        payer_currency: str,
    ):
        self._use_pay_for_currency_conversions = use_pay_for_currency_conversions
        self._pay_quotes = PayQuotes(pay_client)
        self._payer_id = payer_id
        self._payer_currency = payer_currency

    async def handle_offer_search_result(
        self,
        message: TripOfferSearchResult,
        session_token: str,
    ) -> TripOfferSearchResult:
        if self._use_pay_for_currency_conversions:
            message = await self._pay_quotes.get_offer_search_quotes(
                message,
                session_token,
                self._payer_id,
                self._payer_currency,
            )
        return message

    async def handle_price_quote_result(
        self,
        message: TripPriceQuoteResult,
        session_token: str,
    ) -> TripPriceQuoteResult:
        if self._use_pay_for_currency_conversions:
            message = await self._pay_quotes.get_price_quote_quotes(
                message,
                session_token,
                self._payer_id,
                self._payer_currency,
            )
        return message
