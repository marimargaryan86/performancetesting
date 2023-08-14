import httpx
import pytest_httpx
from starlette import status

from snowfall.project.junction.extensions.service.mobile_api import conftest


class TestOffersQuotes(object):
    async def test_offer_quote_created(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        httpx_mock.add_response(
            **await conftest.load_response_fixture("POST_OFFERS_QUOTES.json"),
        )
        response = await authenticated_http_client.post(
            "/offers/quotes",
            headers={"Session-Token": "FMSXrOAhIOdvIbxAmfSt7vJtRBkurNbn"},
            json={
                "data": {
                    "type": "trip-offer-price-quotes",
                    "attributes": {},
                    "relationships": {
                        "offer": {
                            "data": {
                                "id": "04f83af9-90bb-4a0f-9881-03e1e690f7f5",
                                "type": "offers",
                            },
                        },
                        "options": {
                            "data": [
                                {
                                    "id": "04f83af9-90bb-4a0f-9881-03e1e690f7f5",
                                    "type": "offer-options",
                                },
                            ],
                        },
                    },
                },
            },
        )
        assert response.status_code == status.HTTP_201_CREATED

    async def test_get_offer_quote(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        httpx_mock.add_response(
            **await conftest.load_response_fixture("GET_OFFERS_QUOTES_{ID}.json"),
        )

        response = await authenticated_http_client.get(
            "/offers/quotes/04f83af9-90bb-4a0f-9881-03e1e690f7f5",
            headers={"Session-Token": "FMSXrOAhIOdvIbxAmfSt7vJtRBkurNbn"},
        )
        assert response.status_code == status.HTTP_200_OK
