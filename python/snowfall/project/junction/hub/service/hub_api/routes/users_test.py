import httpx
from starlette import status

from snowfall.project.junction.hub.service.hub_api.conftest import RESELLER_ID


class TestUserDataIncludesCompanyAndContacts(object):
    async def test_user_data_includes_company_and_contacts(
        self,
        users_client: httpx.AsyncClient,
    ) -> None:
        resp = await users_client.get("/users/me")
        assert resp.status_code == status.HTTP_200_OK

        body = resp.json()
        user_data = body["data"]

        assert user_data["id"] == RESELLER_ID
        assert user_data["attributes"]["company"]["name"] == "Company name"
        assert len(user_data["attributes"]["contacts"]) == 1
