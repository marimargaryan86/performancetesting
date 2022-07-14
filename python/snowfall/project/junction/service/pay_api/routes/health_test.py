import httpx
from starlette import status


class TestHealth(object):
    async def test_health_status_code(self, http_client: httpx.AsyncClient) -> None:
        response = await http_client.get("/health")
        assert response.status_code == status.HTTP_200_OK
