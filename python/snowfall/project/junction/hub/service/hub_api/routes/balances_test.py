import httpx

from snowfall.project.pay.service.companies.v1alpha.models_pb2 import Account
from snowfall.stdlib import money
from snowfall.stdlib.format import jsonapi
from snowfall.vendor.currency_cloud.models.balance import BalanceResponse


class TestBalances(object):
    async def test_post_currency_account(
        self,
        client: httpx.AsyncClient,
        balance: BalanceResponse,
        account: Account,
    ) -> None:
        request_data = {
            "data": {
                "type": "balances",
                "relationships": {
                    "currency": {
                        "data": {
                            "id": balance.currency,
                            "type": "currencies",
                        },
                    },
                },
            },
        }
        response = await client.post(
            "/accounts/{0}/relationships/currencies".format(balance.account_id),
            json=request_data,
        )

        payload = response.json()["data"]
        flatten_payload = jsonapi.flatten_resource(payload)
        assert payload["id"] == balance.identifier
        assert (
            flatten_payload["amount"]
            == money.from_string(
                balance.amount,
                money.Currency(balance.currency),
            ).amount
        )
        assert flatten_payload["account"] == balance.account_id
        assert flatten_payload["currency"] == balance.currency
