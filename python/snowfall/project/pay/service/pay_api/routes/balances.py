import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.pay.service.accounts import accounts
from snowfall.project.pay.service.pay_api import resources
from snowfall.stdlib.integration.starlette import messages, models
from snowfall.vendor.currency_cloud.client import PaymentClient


class Balances(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        accounts_repository: accounts.AccountsRepository = lagom.injectable,
        contact_person_repository: accounts.ContactPersonsRepository = lagom.injectable,
        payment_client: PaymentClient = lagom.injectable,
    ) -> responses.Response:
        account = await accounts_repository.find_by_id(
            request.path_params["accountId"],
        )

        if not account:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        contact = await contact_person_repository.find_by_id(account.contact_id)

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
