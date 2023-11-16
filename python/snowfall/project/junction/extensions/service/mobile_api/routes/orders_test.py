from typing import Any
from unittest import mock

import httpx
import pytest
import pytest_httpx
import stripe
from starlette import status

from snowfall.project.junction.extensions.service.mobile_api import (
    conftest,
    payments,
    repository,
)
from snowfall.project.junction.extensions.service.mobile_api.tasks import orders

_ORDER_ID = "04f83af9-90bb-4a0f-9881-03e1e690f7f5"


class TestOrders(object):
    async def create_order(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> httpx.Response:
        httpx_mock.add_response(
            **await conftest.load_response_fixture("POST_ORDERS.json"),
        )
        httpx_mock.add_response(
            **await conftest.load_response_fixture("GET_ORDERS_{ID}.json"),
        )
        httpx_mock.add_response(
            **await conftest.load_response_fixture("GET_OFFERS_QUOTES_{ID}.json"),
        )
        httpx_mock.add_response(
            **await conftest.load_response_fixture("POST_REGISTER.json"),
        )

        payments.cancel = mock.AsyncMock()
        payments.capture = mock.AsyncMock()

        orders.send_booking_confirmation = mock.AsyncMock()

        def mock_stripe_retrieve(  # noqa: WPS430
            *args: Any,
            **kwargs: Any,
        ) -> dict[str, Any]:
            return {
                "currency": "EUR",
                "status": "requires_capture",
                "amount": 1337,
            }

        def mock_anything(*args: Any, **kwargs: Any) -> None:  # noqa: WPS430
            """Do nothing."""

        monkeypatch.setattr(stripe.PaymentIntent, "retrieve", mock_stripe_retrieve)
        monkeypatch.setattr(stripe.PaymentIntent, "cancel", mock_anything)
        monkeypatch.setattr(stripe.PaymentIntent, "modify", mock_anything)

        return await authenticated_http_client.post(
            "/orders",
            json={
                "data": {
                    "type": "orders",
                    "attributes": {
                        "contactDetails": {
                            "email": "john.smith@example.com",
                            "address": {
                                "addressLines": ["Street name 7"],
                                "countryCode": "GB",
                                "postalCode": "12345",
                                "city": "London",
                            },
                            "phoneNumber": "+306946661759",
                        },
                        "passengers": [
                            {
                                "firstName": "John",
                                "lastName": "Smith",
                                "title": "mr",
                                "gender": "male",
                                "dateOfBirth": "1980-02-03",
                                "travelerDocument": {
                                    "documentType": "passport",
                                    "documentNumber": "05433434",
                                    "documentIssueCountry": "GB",
                                    "documentExpirationDate": "2025-02-03",
                                    "nationality": "GB",
                                    "residenceCountryCode": "NL",
                                },
                            },
                        ],
                    },
                    "relationships": {
                        "payment": {
                            "data": {
                                "id": "pi_1DseBB2eZvKYlo2Cj8MBORJk",
                                "type": "payments",
                            },
                        },
                        "quote": {
                            "data": {
                                "id": "04f83af9-90bb-4a0f-9881-03e1e690f7f5",
                                "type": "trip-offer-price-quotes",
                            },
                        },
                    },
                },
            },
        )

    async def test_order_created(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        response = await self.create_order(
            authenticated_http_client,
            httpx_mock,
            monkeypatch,
        )
        assert response.status_code == status.HTTP_201_CREATED

    async def test_get_order(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
        orders_repository: repository.OrdersRepository,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        await self.create_order(authenticated_http_client, httpx_mock, monkeypatch)
        response = await authenticated_http_client.get(
            "/orders/{0}".format(_ORDER_ID),
        )

        assert response.json()["data"]["relationships"]["payment"][  # noqa: WPS219
            "data"
        ]["id"]
        assert response.status_code == 200

    async def test_get_order_with_markup(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        await self.create_order(authenticated_http_client, httpx_mock, monkeypatch)
        await _create_markups(authenticated_http_client)

        response = await authenticated_http_client.get(
            "/orders/{0}".format(_ORDER_ID),
        )

        assert response.json()["data"]["relationships"]["markup"][  # noqa: WPS219
            "data"
        ]["id"]
        assert response.status_code == 200

    async def test_get_user_orders(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
        orders_repository: repository.OrdersRepository,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        await self.create_order(authenticated_http_client, httpx_mock, monkeypatch)
        response = await authenticated_http_client.get(
            "/orders",
        )

        assert response.json()["data"][0]["relationships"]["payment"][  # noqa: WPS219
            "data"
        ]["id"]
        assert response.status_code == 200

    async def test_get_user_orders_with_markup(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        await self.create_order(authenticated_http_client, httpx_mock, monkeypatch)
        await _create_markups(authenticated_http_client)

        response = await authenticated_http_client.get(
            "/orders",
        )

        assert response.json()["data"][0]["relationships"]["markup"][  # noqa: WPS219
            "data"
        ]["id"]
        assert response.status_code == 200

    async def test_create_cancellation_request(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        httpx_mock.add_response(
            **await conftest.load_response_fixture("GET_BOOKINGS_{ID}.json"),
        )
        httpx_mock.add_response(
            **await conftest.load_response_fixture("POST_CANCELLATIONS_REQUESTS.json"),
        )
        await self.create_order(authenticated_http_client, httpx_mock, monkeypatch)

        response = await authenticated_http_client.post(
            "/cancellations/requests",
            json={
                "data": {
                    "type": "cancellation-request",
                    "relationships": {
                        "bookings": {
                            "data": [
                                {
                                    "id": "04f83af9-90bb-4a0f-9881-03e1e690f7f5",
                                    "type": "trip-bookings",
                                },
                            ],
                        },
                    },
                },
            },
        )

        assert response.json()["data"]
        assert response.status_code == 201

    async def test_create_cancellation_request_mobile_order_not_found_throws404(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        httpx_mock.add_response(
            **await conftest.load_response_fixture("GET_BOOKINGS_{ID}.json"),
        )

        response = await authenticated_http_client.post(
            "/cancellations/requests",
            json={
                "data": {
                    "type": "cancellation-request",
                    "relationships": {
                        "bookings": {
                            "data": [
                                {
                                    "id": "04f83af9-90bb-4a0f-9881-03e1e690f7f5",
                                    "type": "trip-bookings",
                                },
                            ],
                        },
                    },
                },
            },
        )

        assert response.status_code == 404

    async def test_get_cancellation_request(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        httpx_mock.add_response(
            **await conftest.load_response_fixture(
                "GET_CANCELLATIONS_REQUESTS_{ID}.json",
            ),
        )

        response = await authenticated_http_client.get(
            "/cancellations/requests/d6cfe9e8-bbc9-485f-912f-7ba97ab2cf34",
        )

        assert response.json()["data"]
        assert response.status_code == 200

    async def test_create_markups(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        await self.create_order(authenticated_http_client, httpx_mock, monkeypatch)

        response = await _create_markups(authenticated_http_client)

        assert response.json()["data"]
        assert response.status_code == 201

    async def test_create_markups_mobile_order_not_found_throws404(
        self,
        authenticated_http_client: httpx.AsyncClient,
    ) -> None:
        response = await _create_markups(authenticated_http_client)

        assert response.status_code == 404

    async def test_create_markups_duplicate_order_throws400(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        await self.create_order(authenticated_http_client, httpx_mock, monkeypatch)

        await _create_markups(authenticated_http_client)

        response = await _create_markups(authenticated_http_client)

        assert response.status_code == 400

    async def test_get_markup_by_order(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        await self.create_order(authenticated_http_client, httpx_mock, monkeypatch)

        await _create_markups(authenticated_http_client)

        response = await authenticated_http_client.get(
            "/orders/{0}/markup".format(_ORDER_ID),
        )

        assert response.json()["data"]
        assert response.status_code == 200

    async def test_get_markup_by_order_not_found_throws404(
        self,
        authenticated_http_client: httpx.AsyncClient,
    ) -> None:
        response = await authenticated_http_client.get(
            "/orders/{0}/markup".format(_ORDER_ID),
        )

        assert response.status_code == 404


async def _create_markups(
    authenticated_http_client: httpx.AsyncClient,
) -> httpx.Response:
    return await authenticated_http_client.post(
        "/orders/markups",
        json={
            "data": {
                "type": "markups",
                "attributes": {
                    "serviceFee": {"currency": "EUR", "amount": "13.37"},
                    "agencyMarkup": {"currency": "EUR", "amount": "13.37"},
                    "totalToCollect": {"currency": "EUR", "amount": "13.37"},
                },
                "relationships": {
                    "order": {
                        "data": {
                            "id": _ORDER_ID,
                            "type": "orders",
                        },
                    },
                },
            },
        },
    )
