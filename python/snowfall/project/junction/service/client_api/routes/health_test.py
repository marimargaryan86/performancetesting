import httpx
from starlette import status


class TestHealth(object):
    async def test_health_status_code(self, client: httpx.AsyncClient) -> None:
        response = await client.get("/health")
        assert response.status_code == status.HTTP_200_OK

    async def test_health_status_code_unauthorized(
        self,
        unauthorized_client: httpx.AsyncClient,
    ) -> None:
        response = await unauthorized_client.get("/health")
        assert response.status_code == status.HTTP_200_OK
