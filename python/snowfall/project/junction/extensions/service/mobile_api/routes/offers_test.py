import httpx
import pytest_httpx
from starlette import status

from snowfall.project.junction.extensions.service.mobile_api import conftest


class TestOffers(object):
    async def test_offer_search_created(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        httpx_mock.add_response(
            **await conftest.load_response_fixture("POST_OFFERS_SEARCHES.json"),
        )

        # Test session token in header (deprecated)
        response = await authenticated_http_client.post(
            "/offers/searches",
            headers={"Session-Token": "FMSXrOAhIOdvIbxAmfSt7vJtRBkurNbn"},
            json={
                "data": {
                    "type": "trip-offer-searches",
                    "attributes": {
                        "passengers": [{"dateOfBirth": "1990-02-03"}],
                    },
                    "relationships": {
                        "trips": {
                            "data": [
                                {
                                    "id": "22b8ec9c-0938-51bd-a785-f9242e84af18",
                                    "type": "trips",
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
            "/offers/searches",
            json={
                "data": {
                    "type": "trip-offer-searches",
                    "attributes": {
                        "sessionToken": "FMSXrOAhIOdvIbxAmfSt7vJtRBkurNbn",
                        "passengers": [{"dateOfBirth": "1990-02-03"}],
                    },
                    "relationships": {
                        "trips": {
                            "data": [
                                {
                                    "id": "22b8ec9c-0938-51bd-a785-f9242e84af18",
                                    "type": "trips",
                                },
                            ],
                        },
                    },
                },
            },
        )
        assert response.status_code == status.HTTP_201_CREATED

        # Assert no session token creates an error
        response = await authenticated_http_client.post(
            "/offers/searches",
            json={
                "data": {
                    "type": "trip-offer-searches",
                    "attributes": {
                        "passengers": [{"dateOfBirth": "1990-02-03"}],
                    },
                    "relationships": {
                        "trips": {
                            "data": [
                                {
                                    "id": "22b8ec9c-0938-51bd-a785-f9242e84af18",
                                    "type": "trips",
                                },
                            ],
                        },
                    },
                },
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_get_offer_search_offers(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        httpx_mock.add_response(
            **await conftest.load_response_fixture(
                "GET_OFFERS_SEARCHES_{ID}_OFFERS.json",
            ),
        )

        response = await authenticated_http_client.get(
            "/offers/searches/{offerSearchId}/offers".format(
                offerSearchId="04f83af9-90bb-4a0f-9881-03e1e690f7f5",
            ),
        )

        assert response.status_code == status.HTTP_200_OK

    async def test_get_offer(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        httpx_mock.add_response(
            **await conftest.load_response_fixture(
                "GET_OFFER_{ID}.json",
            ),
        )

        response = await authenticated_http_client.get(
            "/offers/{offerId}".format(
                offerId="04f83af9-90bb-4a0f-9881-03e1e690f7f5",
            ),
        )

        assert response.status_code == status.HTTP_200_OK
