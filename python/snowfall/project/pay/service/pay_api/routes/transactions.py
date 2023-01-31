import lagom
from starlette import endpoints, requests, status

from snowfall.project.pay.service.pay_api import repositories, resources
from snowfall.project.pay.service.quotations import quotations
from snowfall.project.pay.service.transactions.v1alpha.models_pb2 import Transaction
from snowfall.stdlib.integration.starlette import messages, models, request_helpers


class Transactions(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        transaction_repository: repositories.TransactionRepository = lagom.injectable,
        quotation_repository: quotations.QuotationsRepository = lagom.injectable,
    ) -> models.JsonApiResponse:
        body = await request_helpers.flatten_request(request)
        if await quotation_repository.find_by_id(body["quotation"]):
            transaction = await transaction_repository.insert(
                Transaction(
                    external_reference_id=body["externalReference"],
                    quotation_id=body["quotation"],
                    parent_external_id=body["parentExternalReference"],
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
