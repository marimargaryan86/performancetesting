import uuid

from snowfall.project.junction.go.service.offers import offers
from snowfall.project.junction.go.service.offers.pay_quotes_models import (
    PayQuoteAttributes,
    PayQuoteResponse,
)
from snowfall.project.junction.go.service.offers.v1 import models_pb2
from snowfall.project.junction.go.service.offers.v1.amqp_pb2 import (
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

    async def get_offer_search_quotes(  # noqa: WPS210
        self,
        search_result: TripOfferSearchResult,
        session_token: str,
        payer_id: str,
        to_currency: str,
    ) -> TripOfferSearchResult:
        for offer in search_result.offer.offers:
            amount, tax_amount, currency = self._get_amount_tax_and_currency(
                offer,
            )

            quote = await self._get_quote(
                amount=amount,
                session_token=session_token,
                payer_id=payer_id,
                beneficiary_id=search_result.provider_company_id,
                from_currency=currency,
                to_currency=to_currency,
                tax=tax_amount,
            )

            converted_to_currency = money.Currency(to_currency)
            converted_total_amount = money.Money(
                amount=quote.data.attributes.total_amount,
                currency=converted_to_currency,
            )
            offer.price.CopyFrom(converted_total_amount.protobuf())

            while offer.price_breakdown:
                offer.price_breakdown.pop()
            offer.price_breakdown.extend(
                self._build_converted_price_breakdown(
                    quote.data.attributes,
                    converted_to_currency,
                ),
            )
            offer.initial_offer_id = offer.id
            offer.id = string.to_uuid(session_token, uuid.UUID(offer.id))

        search_result.offer.id = string.to_uuid(
            session_token,
            uuid.UUID(search_result.offer.id),
        )
        return search_result

    async def get_price_quote_quotes(  # noqa: WPS210
        self,
        session_token: str,
        search_result: TripPriceQuoteResult,
        payer_id: str,
    ) -> TripPriceQuoteResult:
        amount, tax_amount, currency = self._get_amount_tax_and_currency(
            search_result.price_quote,
        )

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
                amount=amount,
                session_token=session_token,
                payer_id=payer_id,
                beneficiary_id=search_result.provider_company_id,
                from_currency=currency,
                to_currency=offer_option.price.currency_code,
                tax=tax_amount,
            )
        ).data

        search_result.price_quote.pay_quote_id = quote.id

        converted_to_currency = money.Currency(quote.relationships.to_currency.data.id)
        converted_total_amount = money.Money(
            amount=quote.attributes.total_amount,
            currency=converted_to_currency,
        )
        search_result.price_quote.price.CopyFrom(converted_total_amount.protobuf())

        while search_result.price_quote.price_breakdown:
            search_result.price_quote.price_breakdown.pop()
        search_result.price_quote.price_breakdown.extend(
            self._build_converted_price_breakdown(
                quote.attributes,
                converted_to_currency,
            ),
        )

        return search_result

    def _get_amount_tax_and_currency(
        self,
        quote_or_offer: models_pb2.PriceQuote | models_pb2.Offer,
    ) -> tuple[int, int | None, str]:
        base_fare, tax = None, None
        for breakdown in quote_or_offer.price_breakdown:
            match breakdown.breakdown_type:
                case models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE:
                    base_fare = money.from_protobuf(breakdown.price)
                case models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_TAX:
                    tax = money.from_protobuf(breakdown.price)

        if not base_fare or base_fare.amount == 0:
            base_fare = money.from_protobuf(quote_or_offer.price)

        return base_fare.amount, tax.amount if tax else None, base_fare.currency.code

    async def _get_quote(  # noqa: WPS211
        self,
        amount: int,
        session_token: str,
        payer_id: str,
        beneficiary_id: str,
        from_currency: str,
        to_currency: str,
        tax: int | None = None,
    ) -> PayQuoteResponse:
        resp = await self._pay_client.create_quote(
            amount=amount,
            external_reference=session_token,
            payer_id=payer_id,
            beneficiary_id=beneficiary_id,
            from_currency=from_currency,
            to_currency=to_currency,
            tax=tax,
        )
        return PayQuoteResponse(**resp)

    def _build_converted_price_breakdown(
        self,
        pay_quote_attributes: PayQuoteAttributes,
        converted_to_currency: money.Currency,
    ) -> list[models_pb2.PriceBreakdown]:
        price_breakdown = list[models_pb2.PriceBreakdown](
            [
                models_pb2.PriceBreakdown(
                    price=money.Money(
                        amount=pay_quote_attributes.amount,
                        currency=converted_to_currency,
                    ).protobuf(),
                    breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
                ),
            ],
        )

        # TODO: add BREAKDOWN_SERVICE_MARK_UP (pay needs to fix on their end first)

        if pay_quote_attributes.tax:
            price_breakdown.append(
                models_pb2.PriceBreakdown(
                    price=money.Money(
                        amount=pay_quote_attributes.tax,
                        currency=converted_to_currency,
                    ).protobuf(),
                    breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_TAX,
                ),
            )

        if pay_quote_attributes.reseller_markup:
            price_breakdown.append(
                models_pb2.PriceBreakdown(
                    price=money.Money(
                        amount=pay_quote_attributes.reseller_markup,
                        currency=converted_to_currency,
                    ).protobuf(),
                    breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_RESELLER_MARK_UP,
                ),
            )

        if pay_quote_attributes.lead_company_markup:
            price_breakdown.append(
                models_pb2.PriceBreakdown(
                    price=money.Money(
                        amount=pay_quote_attributes.lead_company_markup,
                        currency=converted_to_currency,
                    ).protobuf(),
                    breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_COMPANY_MARK_UP,
                ),
            )

        return price_breakdown


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
