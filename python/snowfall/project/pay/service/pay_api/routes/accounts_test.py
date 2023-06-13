from collections.abc import Sequence
from unittest import mock

import httpx
from starlette import status

from snowfall.project.pay.service.accounts.v1alpha.models_pb2 import Account, Contact


class TestAccounts(object):
    async def test_missing_contact(
        self,
        admin_client: httpx.AsyncClient,
    ) -> None:
        request = {
            "data": {
                "type": "accounts",
                "attributes": {"name": "account"},
                "relationships": {
                    "contact": {
                        "data": {
                            "id": "04f83af5-10bb-4a0f-1881-03e1e660f0f5",
                            "type": "contacts",
                        },
                    },
                },
            },
        }
        response = await admin_client.post("/accounts", json=request)
        error = response.json()["errors"][0]
        assert error["detail"] == "Contact does not exists"
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_contact_with_bad_company_id(
        self,
        admin_client: httpx.AsyncClient,
        contact_with_bad_company_id: Contact,
    ) -> None:
        request = {
            "data": {
                "type": "accounts",
                "attributes": {"name": "account"},
                "relationships": {
                    "contact": {
                        "data": {
                            "id": contact_with_bad_company_id.id,
                            "type": "contacts",
                        },
                    },
                },
            },
        }
        response = await admin_client.post("/accounts", json=request)
        error = response.json()["errors"][0]
        assert error["detail"] == "Contact missing company"
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_list_accounts(
        self,
        admin_client: httpx.AsyncClient,
        accounts_based_on_cc_accounts: Sequence[Account],
        accounts_list_from_cc: Sequence[mock.Mock],
    ) -> None:
        response = await admin_client.get("/accounts")
        payload = response.json()["data"]
        assert len(payload) == len(accounts_list_from_cc)

        for payload_item in payload:
            assert payload_item["id"]
            assert payload_item["attributes"]["status"] == "enabled"
            assert payload_item["relationships"]["company"]["data"]["id"] != "unknown"
