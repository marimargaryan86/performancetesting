import uuid

from snowfall.project.junction.go.adapter import errors
from snowfall.project.junction.go.service.offers import offers
from snowfall.project.junction.go.service.offers.v1 import models_pb2
from snowfall.project.junction.go.service.offers.v1.amqp_pb2 import (
    TripOfferSearchResult,
    TripPriceQuoteResult,
)
from snowfall.project.pay.adapter import companies, quotations
from snowfall.project.pay.service.companies.v1 import models_pb2 as companies_models_pb2
from snowfall.project.pay.service.transactions.v1 import (
    models_pb2 as transactions_models_pb2,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.logging import stdout


class SkippedConversionError(Exception):
    """Raised when a conversion is skipped."""


class PayCreateQuoteError(Exception):
    """Raised when an error occurs creating a quote in PAY."""


class OfferRetrievalError(Exception):
    """Raised when an error occurs retrieving an offer."""


class PayQuotes(object):
    def __init__(
        self,
        quotations_client: quotations.Client,
        companies_client: companies.Client,
        offer_options_repository: offers.OfferOptionsRepository,
        offer_searches_repository: offers.OfferSearchRepository,
        offer_aggregate_repository: offers.OfferAggregateMappingRepository,
    ):
        self._quotations_client = quotations_client
        self._companies_client = companies_client
        self._offer_options_repository = offer_options_repository
        self._offer_searches_repository = offer_searches_repository
        self._offer_aggregate_repository = offer_aggregate_repository
        self._logger = stdout.get_logger()

    async def get_offer_search_quotes(
        self,
        search_result: TripOfferSearchResult,
        session_token: str,
        payer_id: str,
        to_currency: str,
    ) -> TripOfferSearchResult:
        passenger_number = await self._get_passenger_number(
            search_result.offer_search_id,
        )
        for offer in search_result.offer.offers:
            amount, tax_amount, currency = self._get_amount_tax_and_currency(
                offer,
            )
            num_segments = len(offer.segment_details)
            payer_company = await self._get_company(company_id=payer_id)
            beneficiary_company = await self._get_company(
                company_id=search_result.provider_company_id,
            )
            quote = await self._create_quote(
                amount=amount,
                fee_multiplier=num_segments * passenger_number,
                session_token=session_token,
                payer_company=payer_company,
                beneficiary_company=beneficiary_company,
                from_currency=currency,
                to_currency=to_currency,
                tax=tax_amount,
            )

            offer.price.CopyFrom(quote.amounts.total_amount)

            while offer.price_breakdown:
                offer.price_breakdown.pop()
            offer.price_breakdown.extend(
                self._build_converted_price_breakdown(quote.amounts),
            )
            offer.initial_offer_id = offer.id
            offer.id = string.to_uuid(session_token, uuid.UUID(offer.id))

        search_result.offer.id = string.to_uuid(
            session_token,
            uuid.UUID(search_result.offer.id),
        )
        return search_result

    async def get_price_quote_quotes(  # noqa: WPS217
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

        payer_company = await self._get_company(company_id=payer_id)
        offer_search_id = await self._get_offer_search_id(
            search_result.price_quote.option_id,
        )
        passenger_number = await self._get_passenger_number(offer_search_id)

        num_segments = len(offer_option.segment_details)
        beneficiary_company = await self._get_company(
            company_id=search_result.provider_company_id,
        )

        quote = await self._create_quote(
            amount=amount,
            fee_multiplier=passenger_number * num_segments,
            session_token=session_token,
            payer_company=payer_company,
            beneficiary_company=beneficiary_company,
            from_currency=currency,
            to_currency=offer_option.price.currency_code,
            tax=tax_amount,
        )

        search_result.price_quote.pay_quote_id = quote.id

        search_result.price_quote.price.CopyFrom(quote.amounts.total_amount)

        while search_result.price_quote.price_breakdown:
            search_result.price_quote.price_breakdown.pop()
        search_result.price_quote.price_breakdown.extend(
            self._build_converted_price_breakdown(quote.amounts),
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

    async def _get_company(
        self,
        company_id: str,
    ) -> companies_models_pb2.Company:
        try:
            return await self._companies_client.get(company_id)
        except errors.NotFoundError as err:
            self._logger.exception(
                "Failed to fetch company in PAY",
                company_id=company_id,
            )
            raise PayCreateQuoteError from err

    async def _get_offer_search_id(self, offer_option_id: str) -> str:
        offers_aggregator = await self._offer_aggregate_repository.find_by_result_id(
            offer_option_id,
        )
        if offers_aggregator is None:
            self._logger.exception(
                "Offers aggregator not found for offer option ID",
                option_id=offer_option_id,
            )
            raise OfferRetrievalError()

        return offers_aggregator.offer_search_id

    async def _get_passenger_number(self, offer_search_id: str) -> int:
        offer_search = await self._offer_searches_repository.find_by_id(offer_search_id)
        if offer_search is None:
            self._logger.exception(
                "Offer search not found for offer search ID",
                offer_search_id=offer_search_id,
            )
            raise OfferRetrievalError()

        if offer_search.HasField("simple_trip"):
            return len(offer_search.simple_trip.passengers)

        if offer_search.HasField("trip"):
            return len(offer_search.trip.passengers)

        return 1

    async def _create_quote(
        self,
        amount: int,
        fee_multiplier: int,
        session_token: str,
        payer_company: companies_models_pb2.Company,
        beneficiary_company: companies_models_pb2.Company,
        from_currency: str,
        to_currency: str,
        tax: int | None = None,
    ) -> transactions_models_pb2.Quotation:
        try:
            return await self._quotations_client.create(
                amount=amount,
                session_token=session_token,
                payer=payer_company,
                beneficiary_company=beneficiary_company,
                from_currency=from_currency,
                to_currency=to_currency,
                tax=tax if tax else 0,
                fee_multiplier=fee_multiplier,
            )
        except (errors.NotFoundError, errors.ServiceUnavailableError) as err:
            self._logger.exception(
                "Failed to create quote in PAY",
                amount=amount,
                session_token=session_token,
                payer_id=payer_company.id,
                beneficiary_id=beneficiary_company.id,
                from_currency=from_currency,
                to_currency=to_currency,
            )
            raise PayCreateQuoteError from err

    def _build_converted_price_breakdown(
        self,
        pay_quote_amounts: transactions_models_pb2.QuotationAmounts,
    ) -> list[models_pb2.PriceBreakdown]:
        price_breakdown = list[models_pb2.PriceBreakdown](
            [
                models_pb2.PriceBreakdown(
                    price=pay_quote_amounts.base_converted,
                    breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
                ),
            ],
        )

        if money.from_protobuf(pay_quote_amounts.tax_converted).amount:
            price_breakdown.append(
                models_pb2.PriceBreakdown(
                    price=pay_quote_amounts.tax_converted,
                    breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_TAX,
                ),
            )

        if money.from_protobuf(pay_quote_amounts.service_markup).amount:
            price_breakdown.append(
                models_pb2.PriceBreakdown(
                    price=pay_quote_amounts.service_markup,
                    breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_SERVICE_MARK_UP,
                ),
            )

        if money.from_protobuf(pay_quote_amounts.fee_amount).amount:
            price_breakdown.append(
                models_pb2.PriceBreakdown(
                    price=pay_quote_amounts.fee_amount,
                    breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_RESELLER_MARK_UP,
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
