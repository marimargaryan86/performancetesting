import httpx
from starlette import status

from snowfall.project.pay.service.accounts.v1alpha.models_pb2 import ContactPerson


class TestAccounts(object):
    async def test_missing_contact_person(
        self,
        client: httpx.AsyncClient,
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
        response = await client.post("/accounts", json=request)
        error = response.json()["errors"][0]
        assert error["detail"] == "Contact person does not exists"
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_contact_person_with_bad_company_id(
        self,
        client: httpx.AsyncClient,
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
        response = await client.post("/accounts", json=request)
        error = response.json()["errors"][0]
        assert error["detail"] == "Contact person missing company"
        assert response.status_code == status.HTTP_400_BAD_REQUEST
