import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.pay.adapter import accounts as accounts_adapter
from snowfall.project.pay.service.accounts import repositories
from snowfall.project.pay.service.pay_api import resources
from snowfall.project.pay.service.pay_api.repositories import CurrencyRepository
from snowfall.stdlib.integration.starlette import messages, models, request_helpers
from snowfall.vendor.currency_cloud.client import PaymentClient
from snowfall.vendor.currency_cloud.models.balance import BalanceRequest


class Balances(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        accounts_client: accounts_adapter.GrpcClient = lagom.injectable,
        contact_repository: repositories.ContactsRepository = lagom.injectable,
        payment_client: PaymentClient = lagom.injectable,
    ) -> responses.Response:
        account = await accounts_client.get(
            request.path_params["accountId"],
        )

        if not account:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        contact = await contact_repository.find_by_id(account.contact_id)

        if not contact:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        balances = payment_client.get_balances(contact.external_reference)

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.BalanceResource.from_model(balance)
                    for balance in balances
                ],
            ),
            request=request,
        )

    async def post(  # noqa: WPS211
        self,
        request: requests.Request,
        accounts_client: accounts_adapter.GrpcClient = lagom.injectable,
        contacts_repository: repositories.ContactsRepository = lagom.injectable,
        currencies_repository: CurrencyRepository = lagom.injectable,
        payment_client: PaymentClient = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        account = await accounts_client.get(
            request.path_params["accountId"],
        )

        if not account:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        contact = await contacts_repository.find_by_id(account.contact_id)
        if not contact:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        if not currencies_repository.find_by_id(body["currency"]):
            return models.JsonApiResponse(
                models.Body(
                    errors=[
                        models.Error(
                            status=str(status.HTTP_404_NOT_FOUND),
                            code="not_found",
                            detail="currency not found",
                            source=models.ErrorSourcePointer(
                                pointer="/data/relationships/currency/data/id",
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_404_NOT_FOUND,
            )

        balance = payment_client.add_currency_into_account(
            BalanceRequest(
                currency=body["currency"],
                on_behalf_of=contact.external_reference,
            ),
        )

        return await messages.create_response(
            models.Body(
                data=resources.BalanceResource.from_model(
                    balance=balance,
                ),
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )
