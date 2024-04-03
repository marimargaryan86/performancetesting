import httpx
import pytest_httpx
from starlette import status

from snowfall.project.junction.extensions.service.mobile_api import conftest


class TestHandlers:
    async def test_go_errors_forwarded(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        httpx_mock.add_response(
            **await conftest.load_response_fixture(
                "GET_TRIPS_SEARCHES_{ID}_TRIPS_404.json",
            ),
        )

        response = await authenticated_http_client.get(
            "/trips/searches/507db9cc-0417-4267-bace-e29b3845f42b/trips",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
