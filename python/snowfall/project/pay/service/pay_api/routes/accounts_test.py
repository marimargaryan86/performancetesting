from typing import Sequence
from unittest import mock

import httpx
from starlette import status

from snowfall.project.pay.service.accounts.v1alpha.models_pb2 import (
    Account,
    ContactPerson,
)


class TestAccounts(object):
    async def test_missing_contact_person(
        self,
        admin_client: httpx.AsyncClient,
    ) -> None:
        request = {
            "data": {
                "type": "accounts",
                "attributes": {"name": "account"},
                "relationships": {
                    "contactPerson": {
                        "data": {
                            "id": "04f83af5-10bb-4a0f-1881-03e1e660f0f5",
                            "type": "contact-persons",
                        },
                    },
                },
            },
        }
        response = await admin_client.post("/accounts", json=request)
        error = response.json()["errors"][0]
        assert error["detail"] == "Contact person does not exists"
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_contact_person_with_bad_company_id(
        self,
        admin_client: httpx.AsyncClient,
        contact_person_with_bad_company_id: ContactPerson,
    ) -> None:
        request = {
            "data": {
                "type": "accounts",
                "attributes": {"name": "account"},
                "relationships": {
                    "contactPerson": {
                        "data": {
                            "id": contact_person_with_bad_company_id.id,
                            "type": "contact-persons",
                        },
                    },
                },
            },
        }
        response = await admin_client.post("/accounts", json=request)
        error = response.json()["errors"][0]
        assert error["detail"] == "Contact person missing company"
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

        for index, account in enumerate(accounts_list_from_cc):
            payload_item = payload[index]
            assert payload_item["id"]
            assert payload_item["attributes"]["name"] == account.account_name
            assert payload_item["attributes"]["status"] == "enabled"
            assert payload_item["relationships"]["company"]["data"]["id"] != "unknown"
