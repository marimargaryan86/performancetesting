import httpx
from starlette import status

from snowfall import fixtures


class TestSegments(object):
    async def test_segment_unauthorized(self, client: httpx.AsyncClient) -> None:
        client.headers["Authorization"] = "invalid"
        response = await client.get("/segments/{id}".format(id=fixtures.SEGMENTS[0]))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_unknown_segment_returns_not_found(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get("/segments/{id}".format(id=fixtures.NOT_FOUND))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_segment_is_found(self, client: httpx.AsyncClient) -> None:
        response = await client.get("/segments/{id}".format(id=fixtures.SEGMENTS[0]))
        assert response.status_code == status.HTTP_200_OK
