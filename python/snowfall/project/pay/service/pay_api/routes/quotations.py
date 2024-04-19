import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.pay.adapter import quotations
from snowfall.project.pay.service.currencies.v1.models_pb2 import Currency
from snowfall.project.pay.service.pay_api import resources
from snowfall.project.pay.service.pay_api.routes import routes_handlers
from snowfall.stdlib.integration.starlette import messages, models, request_helpers


class Quotations(endpoints.HTTPEndpoint):
    @routes_handlers.grpc_errors_handler
    async def post(  # noqa: WPS217
        self,
        request: requests.Request,
        quotations_client: quotations.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        session_token = body.get("externalReference")

        if session_token:
            session_token += request.user.username

        quotation = await quotations_client.create(
            from_currency=body["fromCurrency"],
            to_currency=body["toCurrency"],
            amount=body["amount"],
            # We return with errors above in the case that these are undefined.
            payer_id=body["payer"],
            beneficiary_id=body["beneficiary"],
            session_token=session_token,
            tax=body.get("tax", 0),
            fee_multiplier=body["feeMultiplier"],
            vertical_type=body["verticalType"],
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.QuoteResource.from_proto(
                    quotation=quotation,
                    request=request,
                ),
            ),
            request=request,
        )

    def _validate_currencies(
        self,
        from_currency: Currency | None,
        to_currency: Currency | None,
    ) -> list[models.Error]:
        currency_errors = []
        if not from_currency:
            currency_errors.append(
                models.Error(
                    status=str(status.HTTP_404_NOT_FOUND),
                    code="not_found",
                    detail="Provided currency is not supported",
                    source=models.ErrorSourcePointer(
                        pointer="data/relationships/fromCurrency",
                    ),
                ),
            )
        if not to_currency:
            currency_errors.append(
                models.Error(
                    status=str(status.HTTP_404_NOT_FOUND),
                    code="not_found",
                    detail="Provided currency is not supported",
                    source=models.ErrorSourcePointer(
                        pointer="data/relationships/toCurrency",
                    ),
                ),
            )

        return currency_errors
