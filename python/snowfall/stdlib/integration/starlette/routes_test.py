import httpx
from starlette import status


class TestHealth(object):
    async def test_health_status_code(self, test_client: httpx.AsyncClient) -> None:
        response = await test_client.get("/health")
        assert response.status_code == status.HTTP_200_OK
