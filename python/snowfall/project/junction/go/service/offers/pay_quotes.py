import uuid

from snowfall.project.junction.go.service.offers import offers
from snowfall.project.junction.go.service.offers.pay_quotes_models import (
    PayQuoteResponse,
)
from snowfall.project.junction.go.service.offers.v1alpha import models_pb2
from snowfall.project.junction.go.service.offers.v1alpha.amqp_pb2 import (
    TripOfferSearchResult,
    TripPriceQuoteResult,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.logging import stdout
from snowfall.vendor.junction.pay.client import Client as PayClient


class SkippedConversionError(Exception):
    """Raised when a conversion is skipped."""


class PayQuotes(object):
    def __init__(
        self,
        pay_client: PayClient,
        offer_options_repository: offers.OfferOptionsRepository,
    ):
        self._pay_client = pay_client
        self._offer_options_repository = offer_options_repository
        self._logger = stdout.get_logger()

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
                session_token=session_token,
                payer_id=payer_id,
                beneficiary_id=search_result.provider_company_id,
                from_currency=offer_money.currency.code,
                to_currency=to_currency,
            )

            converted_money = money.Money(
                amount=quote.data.attributes.amount,
                currency=money.Currency(to_currency),
            )

            offer.price.CopyFrom(converted_money.protobuf())
            offer.initial_offer_id = offer.id
            offer.id = string.to_uuid(session_token, uuid.UUID(offer.id))
        search_result.offer.id = string.to_uuid(
            session_token,
            uuid.UUID(search_result.offer.id),
        )
        return search_result

    async def get_price_quote_quotes(
        self,
        session_token: str,
        search_result: TripPriceQuoteResult,
        payer_id: str,
    ) -> TripPriceQuoteResult:
        price_quote_money = money.from_protobuf(search_result.price_quote.price)

        search_result.price_quote.option_id = string.to_uuid(
            session_token,
            uuid.UUID(search_result.price_quote.option_id),
        )

        offer_option = await self._offer_options_repository.find_by_id(
            search_result.price_quote.option_id,
        )

        if not offer_option:
            self._logger.warning(
                "Offer option not found",
                option_id=search_result.option_id,
                price_quote_container_id=search_result.price_quote_container_id,
                quote_option_id=search_result.price_quote.option_id,
                quote_id=search_result.price_quote.id,
            )

            raise SkippedConversionError()

        quote = (
            await self._get_quote(
                amount=price_quote_money.amount,
                session_token=session_token,
                payer_id=payer_id,
                beneficiary_id=search_result.provider_company_id,
                from_currency=price_quote_money.currency.code,
                to_currency=offer_option.price.currency_code,
            )
        ).data

        search_result.price_quote.pay_quote_id = quote.id

        converted_money = money.Money(
            amount=quote.attributes.amount,
            currency=money.Currency(quote.relationships.to_currency.data.id),
        )

        search_result.price_quote.price.CopyFrom(converted_money.protobuf())

        return search_result

    async def _get_quote(  # noqa: WPS211
        self,
        amount: int,
        session_token: str,
        payer_id: str,
        beneficiary_id: str,
        from_currency: str,
        to_currency: str,
    ) -> PayQuoteResponse:
        resp = await self._pay_client.create_quote(
            amount=amount,
            external_reference=session_token,
            payer_id=payer_id,
            beneficiary_id=beneficiary_id,
            from_currency=from_currency,
            to_currency=to_currency,
        )
        return PayQuoteResponse(**resp)


class PayQuoteFetcher(object):
    def __init__(
        self,
        pay_quotes: PayQuotes,
        payer_id: str,
        payer_currency: str,
        *,
        use_pay_for_currency_conversions: bool,
    ):
        self._use_pay_for_currency_conversions = use_pay_for_currency_conversions
        self._pay_quotes = pay_quotes
        self._payer_id = payer_id
        self._payer_currency = payer_currency

    async def handle_offer_search_result(
        self,
        message: TripOfferSearchResult,
        session_token: str,
        offer_search: models_pb2.OfferSearch,
    ) -> TripOfferSearchResult:
        if not self._use_pay_for_currency_conversions:
            return message

        payer_company_id = offer_search.pay_company_id or self._payer_id
        payer_currency = offer_search.currency_code or self._payer_currency

        return await self._pay_quotes.get_offer_search_quotes(
            message,
            session_token,
            payer_company_id,
            payer_currency,
        )

    async def handle_price_quote_result(
        self,
        message: TripPriceQuoteResult,
        price_quote_container: models_pb2.PriceQuoteContainer,
    ) -> TripPriceQuoteResult:
        if not self._use_pay_for_currency_conversions:
            return message

        payer_company_id = price_quote_container.pay_company_id or self._payer_id

        return await self._pay_quotes.get_price_quote_quotes(
            price_quote_container.session_token,
            message,
            payer_company_id,
        )
