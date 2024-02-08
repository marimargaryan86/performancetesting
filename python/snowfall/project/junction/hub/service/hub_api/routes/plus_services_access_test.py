import httpx
from starlette import status


class TestPlusServicesAccess(object):
    async def test_updating_plus_services_access_for_the_reseller(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        request = {
            "data": [
                {
                    "type": "plus-services-access",
                    "attributes": {
                        "ref": "flight_stats_alerts",
                        "enabled": True,
                    },
                },
            ],
        }
        response = await client.patch(
            "/resellers/plus-services-access/04f83af5-10bb-4a0f-1881-03e1e690f0f5",
            json=request,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_getting_plus_services_access_by_reseller_id(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/resellers/plus-services-access/04f83af5-10bb-4a0f-1881-03e1e690f0f5",
        )
        assert response.status_code == status.HTTP_200_OK
