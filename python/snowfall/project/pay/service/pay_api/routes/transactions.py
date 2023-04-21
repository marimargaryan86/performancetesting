import lagom
from starlette import endpoints, exceptions, requests, status

from snowfall.project.pay.service.pay_api import repositories, resources
from snowfall.project.pay.service.quotations import quotations
from snowfall.project.pay.service.quotations.v1alpha.models_pb2 import Quotation
from snowfall.project.pay.service.transactions.v1alpha.models_pb2 import Transaction
from snowfall.stdlib import money, string
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    request_helpers,
)
from snowfall.vendor.currency_cloud.client import PaymentClient
from snowfall.vendor.currency_cloud.errors import CurrencyCloudError
from snowfall.vendor.currency_cloud.models import conversion


class Transactions(endpoints.HTTPEndpoint):
    async def post(  # noqa: WPS210, WPS211, WPS217
        self,
        request: requests.Request,
        payment_client: PaymentClient = lagom.injectable,
        transaction_repository: repositories.TransactionRepository = lagom.injectable,
        quotation_repository: quotations.QuotationsRepository = lagom.injectable,
        conversion_repository: repositories.ConversionRepository = lagom.injectable,
    ) -> models.JsonApiResponse:
        body = await request_helpers.flatten_request(request)
        quot = await quotation_repository.find_by_id(body["quotation"])
        if quot and quot.status == Quotation.Status.STATUS_QUOTED:
            transaction_id = string.uuid()
            are_currencies_same = (
                quot.amounts.base_converted.currency_code
                == quot.amounts.beneficiary.currency_code
            )
            conversion_id = ""
            if not are_currencies_same:
                try:
                    cc_conversion = payment_client.create_conversion(
                        conversion.ConversionRequest(
                            buy_currency=quot.amounts.base_converted.currency_code,
                            sell_currency=quot.amounts.beneficiary.currency_code,
                            amount=money.from_protobuf(quot.amounts.beneficiary).amount,
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
                                    detail=message,
                                )
                                for message in exc.messages
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
                    invoice_reference_id=body["invoiceReference"],
                    conversion_id=conversion_id,
                    amounts=quot.amounts,
                    rates=quot.rates,
                    payer_id=quot.payer_id,
                    beneficiary_id=quot.beneficiary_id,
                ),
            )
            await quotation_repository.update_status(
                quot.id,
                Quotation.Status.STATUS_CONFIRMED,
            )
            return await messages.create_response(
                body=messages.models.Body(
                    data=resources.Transaction.from_proto(
                        transaction=transaction,
                        request=request,
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
                        source=messages.models.ErrorSourcePointer(
                            pointer="/data/relationships/quotation/data/id",
                        ),
                    ),
                ],
            ),
            status_code=status.HTTP_404_NOT_FOUND,
        )

    async def get(
        self,
        request: requests.Request,
        transaction_repository: repositories.TransactionRepository = lagom.injectable,
    ) -> models.JsonApiResponse:
        transaction_id = request.path_params["transactionId"]

        transaction = await transaction_repository.find_by_id(transaction_id)
        if transaction is None:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return await messages.create_response(
            body=models.Body(
                data=resources.Transaction.from_proto(transaction, request),
            ),
            request=request,
        )


class ListTransactions(endpoints.HTTPEndpoint):
    _default_page_size = 20

    async def get(
        self,
        request: requests.Request,
        transaction_repository: repositories.TransactionRepository = lagom.injectable,
    ) -> models.JsonApiResponse:
        pagination = pagination_helpers.get_pagination(request)

        transactions = await transaction_repository.find(
            cursor=pagination.cursor,
        )

        transactions.limit(pagination.limit or self._default_page_size)

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.Transaction.from_proto(transaction, request)
                    async for transaction in transactions
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("ListTransactions"),
                    await transactions.cursor(),
                    pagination,
                ),
            ),
            request=request,
        )
