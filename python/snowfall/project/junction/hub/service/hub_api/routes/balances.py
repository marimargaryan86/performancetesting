import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.hub.service.hub_api import resources
from snowfall.project.pay.adapter import accounts as accounts_adapter
from snowfall.project.pay.adapter import contacts as contacts_adapter
from snowfall.project.pay.adapter import currencies
from snowfall.stdlib.integration.starlette import messages, models, request_helpers
from snowfall.vendor.currency_cloud.client import PaymentClient
from snowfall.vendor.currency_cloud.models.balance import BalanceRequest


class Balances(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        accounts_client: accounts_adapter.Client = lagom.injectable,
        contacts_client: contacts_adapter.Client = lagom.injectable,
        payment_client: PaymentClient = lagom.injectable,
    ) -> responses.Response:
        account = await accounts_client.get(request.path_params["accountId"])

        if not account:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        contact = await contacts_client.get(account.contact_id)

        per_page = 50
        balances = await payment_client.get_balances(
            contact.external_reference,
            per_page=per_page,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.BalanceResource.from_model(balance)
                    for balance in balances
                ],
            ),
            request=request,
        )

    async def post(  # noqa: WPS217
        self,
        request: requests.Request,
        accounts_client: accounts_adapter.Client = lagom.injectable,
        contacts_client: contacts_adapter.Client = lagom.injectable,
        currencies_client: currencies.Client = lagom.injectable,
        payment_client: PaymentClient = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        account = await accounts_client.get(
            request.path_params["accountId"],
        )

        if not account:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        contact = await contacts_client.get(account.contact_id)

        if not await currencies_client.get(body["currency"], no_exist_ok=True):
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

        balance = await payment_client.add_currency_into_account(
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
