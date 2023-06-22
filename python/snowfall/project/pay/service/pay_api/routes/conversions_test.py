import httpx
from starlette import status

from snowfall.project.pay import fixtures


class TestConversions(object):
    async def test_get_conversion_details_success(
        self,
        admin_client: httpx.AsyncClient,
    ) -> None:
        response = await admin_client.get(
            "/conversions/{conversion_id}".format(
                conversion_id=fixtures.CONVERSIONS[0],
            ),
        )

        assert response.status_code == status.HTTP_200_OK

    async def test_get_conversion_details_not_found(
        self,
        admin_client: httpx.AsyncClient,
    ) -> None:
        response = await admin_client.get(
            "/conversions/cd001298-d00e-4114-a385-877fa8801882",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
