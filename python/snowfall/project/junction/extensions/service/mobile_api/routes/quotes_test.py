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

        # Test session token in header (deprecated)
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

        # Test session token in body
        response = await authenticated_http_client.post(
            "/offers/quotes",
            json={
                "data": {
                    "type": "trip-offer-price-quotes",
                    "attributes": {
                        "sessionToken": "FMSXrOAhIOdvIbxAmfSt7vJtRBkurNbn",
                    },
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

        # Test no session token throws error
        response = await authenticated_http_client.post(
            "/offers/quotes",
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
        assert response.status_code == status.HTTP_400_BAD_REQUEST

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
        )

        assert response.status_code == status.HTTP_200_OK
