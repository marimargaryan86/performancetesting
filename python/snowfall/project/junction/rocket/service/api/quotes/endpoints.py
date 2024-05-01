import dataclasses
import datetime
from collections.abc import Mapping

import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.rocket.service.api import errors
from snowfall.project.junction.rocket.service.api.quotes import models as quote_models
from snowfall.project.junction.rocket.service.api.quotes import quotes
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    grpc_pb2 as searches_pb2,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    grpc_pb2_grpc as searches_pb2_grpc,
)
from snowfall.stdlib.integration.starlette import messages, models, request_helpers
from snowfall.stdlib.logging import stdout

_logger = stdout.get_logger()


@dataclasses.dataclass(frozen=True)
class QuotesSettings:
    reseller_currencies: Mapping[str, str]
    reseller_pay_company_mapping: Mapping[str, str]


async def _is_flight_quote(request: requests.Request) -> bool:
    body = await request.json()
    offers_rel = body["data"]["relationships"]["offers"]

    return offers_rel["data"][0]["type"] == "flight-offers"


class Quotes(endpoints.HTTPEndpoint):
    @errors.handle_grpc_errors
    async def post(
        self,
        request: requests.Request,
        quotes_settings: QuotesSettings = lagom.injectable,
        go_quotations: searches_pb2_grpc.QuoteServiceStub = lagom.injectable,
        grpc_timeout: datetime.timedelta = lagom.injectable,
        flight_quotes_manager: quotes.FlightQuoteManager = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        request_offer_ids = list(body["offers"])

        reseller_pay_company_id, reseller_currency = self._get_reseller_config(
            quotes_settings,
            request.user.username,
        )

        if await _is_flight_quote(request):
            return await self._create_flight_quote_response(
                flight_quotes_manager=flight_quotes_manager,
                request=request,
                offer_id=request_offer_ids[0],
                reseller_pay_company_id=reseller_pay_company_id,
                reseller_currency=reseller_currency,
            )

        response: searches_pb2.CreateQuoteResponse = await go_quotations.CreateQuote(
            searches_pb2.CreateQuoteRequest(
                offer_ids=request_offer_ids,
                reseller_id=request.user.username,
                reseller_pay_company_id=reseller_pay_company_id,
                reseller_currency=reseller_currency,
            ),
            timeout=grpc_timeout.total_seconds(),
        )

        return await messages.create_response(
            body=models.Body(
                data=quote_models.QuoteResource.from_proto(
                    response.quote,
                    request,
                ),
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )

    @errors.handle_grpc_errors
    async def get(
        self,
        request: requests.Request,
        grpc_timeout: datetime.timedelta = lagom.injectable,
        go_quotations: searches_pb2_grpc.QuoteServiceStub = lagom.injectable,
    ) -> responses.Response:
        quote_id = request.path_params["quoteId"]

        # TODO(aram.h): handle J1, fetch the quote from the proper place

        response: searches_pb2.GetQuoteResponse = await go_quotations.GetQuote(
            searches_pb2.GetQuoteRequest(id=quote_id),
            timeout=grpc_timeout.total_seconds(),
        )

        return await messages.create_response(
            body=models.Body(
                data=quote_models.QuoteResource.from_proto(
                    response.quote,
                    request,
                ),
            ),
            request=request,
        )

    async def _create_flight_quote_response(
        self,
        flight_quotes_manager: quotes.FlightQuoteManager,
        request: requests.Request,
        offer_id: str,
        reseller_pay_company_id: str,
        reseller_currency: str,
    ) -> models.JsonApiResponse:
        quote = await flight_quotes_manager.create(
            offer_id,
            request.user.username,
            reseller_pay_company_id,
            reseller_currency,
        )

        return await messages.create_response(
            body=models.Body(
                data=quote_models.QuoteResource.from_flight_quote_proto(
                    quote,
                    request,
                ),
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )

    def _get_reseller_config(
        self,
        quotes_settings: QuotesSettings,
        reseller_id: str,
    ) -> tuple[str, str]:
        reseller_pay_company_id = quotes_settings.reseller_pay_company_mapping.get(
            reseller_id,
            "",
        )
        if not reseller_pay_company_id:
            _logger.error(
                "No reseller PAY company id in configuration for reseller",
                reseller_id=reseller_id,
            )
            raise exceptions.HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY)

        reseller_currency = quotes_settings.reseller_currencies.get(reseller_id, "")
        if not reseller_currency:
            _logger.error(
                "No reseller currency in configuration for reseller",
                reseller_id=reseller_id,
            )
            raise exceptions.HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY)

        return (reseller_pay_company_id, reseller_currency)
