import lagom
from starlette import endpoints, requests, status

from snowfall.project.pay.service.pay_api import repositories, resources
from snowfall.project.pay.service.quotations import quotations
from snowfall.project.pay.service.transactions.v1alpha.models_pb2 import Transaction
from snowfall.stdlib import money, string
from snowfall.stdlib.integration.starlette import messages, models, request_helpers
from snowfall.vendor.currency_cloud.client import PaymentClient
from snowfall.vendor.currency_cloud.errors import CurrencyCloudError
from snowfall.vendor.currency_cloud.models import conversion


class Transactions(endpoints.HTTPEndpoint):
    async def post(  # noqa: WPS210, WPS211
        self,
        request: requests.Request,
        payment_client: PaymentClient = lagom.injectable,
        transaction_repository: repositories.TransactionRepository = lagom.injectable,
        quotation_repository: quotations.QuotationsRepository = lagom.injectable,
        conversion_repository: repositories.ConversionRepository = lagom.injectable,
    ) -> models.JsonApiResponse:
        body = await request_helpers.flatten_request(request)
        quot = await quotation_repository.find_by_id(body["quotation"])
        if quot:
            transaction_id = string.uuid()
            are_currencies_same = (
                quot.converted_beneficiary_amount.currency_code
                == quot.beneficiary_amount.currency_code
            )
            conversion_id = ""
            if not are_currencies_same:
                try:
                    cc_conversion = payment_client.create_conversion(
                        conversion.ConversionRequest(
                            buy_currency=quot.converted_beneficiary_amount.currency_code,
                            sell_currency=quot.beneficiary_amount.currency_code,
                            amount=money.from_protobuf(quot.beneficiary_amount).amount,
                            reason=transaction_id,
                        ),
                    )
                except CurrencyCloudError as exc:
                    return models.JsonApiResponse(
                        models.Body(
                            errors=[
                                models.Error(
                                    status=str(exc.status),
                                    code=exc.code,
                                    detail=exc.message,
                                ),
                            ],
                        ),
                        status_code=exc.status,
                    )
                inserted_conversion = await conversion_repository.create(
                    cc_conversion,
                )
                conversion_id = inserted_conversion.id
            transaction = await transaction_repository.insert(
                Transaction(
                    id=transaction_id,
                    external_reference_id=body["externalReference"],
                    parent_external_id=body["parentExternalReference"],
                    conversion_id=conversion_id,
                    beneficiary_amount=quot.beneficiary_amount,
                    exchange_rate=quot.exchange_rate,
                    converted_beneficiary_amount=quot.converted_beneficiary_amount,
                    buffer_rate=quot.buffer_rate,
                    buffer_amount=quot.buffer_amount,
                    sales_rate=quot.sales_rate,
                    sales_amount=quot.sales_amount,
                    offer_amount=quot.offer_amount,
                    payer_id=quot.payer_id,
                    beneficiary_id=quot.beneficiary_id,
                ),
            )

            return await messages.create_response(
                body=messages.models.Body(
                    data=resources.Transaction.from_proto(
                        transaction=transaction,
                    ),
                ),
                request=request,
                status_code=status.HTTP_201_CREATED,
            )
        return models.JsonApiResponse(
            body=messages.models.Body(
                errors=[
                    messages.models.Error(
                        status=str(status.HTTP_404_NOT_FOUND),
                        code="not_found",
                        detail="Quotation not valid",
                        source=messages.models.ErrorSource(
                            pointer="/data/relationships/quotation/data/id",
                        ),
                    ),
                ],
            ),
            status_code=status.HTTP_404_NOT_FOUND,
        )
