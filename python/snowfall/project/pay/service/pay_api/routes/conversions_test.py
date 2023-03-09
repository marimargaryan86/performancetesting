import httpx
from starlette import status

from snowfall.project.pay.service.conversions.v1alpha.models_pb2 import Conversion


class TestConversions(object):
    async def test_get_conversion_details_success(
        self,
        admin_client: httpx.AsyncClient,
        valid_conversion: Conversion,
    ) -> None:
        response = await admin_client.get(
            "/conversions/{conversion_id}".format(conversion_id=valid_conversion.id),
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
