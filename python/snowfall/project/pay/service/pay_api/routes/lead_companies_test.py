import httpx
from starlette import status

from snowfall.project.pay.fixtures import LEAD_COMPANIES
from snowfall.stdlib.integration.starlette import testing


class TestLeadCompanies(object):
    async def test_get_all_lead_companies(
        self,
        admin_client: httpx.AsyncClient,
    ) -> None:
        await testing.test_list_and_view_endpoints(
            client=admin_client,
            url="/lead-companies",
            expected_ids=LEAD_COMPANIES,
        )

    async def test_create_lead_company(
        self,
        admin_client: httpx.AsyncClient,
    ) -> None:
        request = {
            "data": {
                "type": "lead-companies",
                "attributes": {
                    "name": "LeadCompany",
                    "salesMarkups": [
                        {
                            "currency": "EUR",
                            "amount": 1337,
                        },
                    ],
                },
            },
        }

        response = await admin_client.post("/lead-companies", json=request)

        assert response.status_code == status.HTTP_201_CREATED

    async def test_update_lead_company(
        self,
        admin_client: httpx.AsyncClient,
    ) -> None:
        request = {
            "data": {
                "type": "lead-companies",
                "attributes": {
                    "name": "UpdatedLeadCompany",
                    "salesMarkups": [
                        {
                            "currency": "USD",
                            "amount": 2000,
                        },
                    ],
                },
            },
        }

        response = await admin_client.patch(
            "/lead-companies/{0}".format(LEAD_COMPANIES[0]),
            json=request,
        )

        assert response.status_code == status.HTTP_200_OK
