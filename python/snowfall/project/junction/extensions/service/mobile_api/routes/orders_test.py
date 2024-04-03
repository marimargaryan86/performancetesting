from unittest import mock

import httpx
import pytest
import pytest_httpx
from starlette import status

from snowfall.project.junction.extensions.service.mobile_api import (
    conftest,
    repository,
)
from snowfall.project.junction.extensions.service.mobile_api.tasks import orders
from snowfall.project.pay.adapter import credit_card_payment
from snowfall.project.pay.service.payments.v1 import credit_card_models_pb2
from snowfall.stdlib import money

_ORDER_ID = "04f83af9-90bb-4a0f-9881-03e1e690f7f5"


async def pre_setup_credit_card(
    credit_card_payment_client: credit_card_payment.Client,
) -> credit_card_models_pb2.CreditCardPayment:
    credit_card_payment = await credit_card_payment_client.create_credit_card_payment(
        amount=money.Money(1337, money.Currency("EUR")),
        credit_card_holder_id="credit_card_holder_id",
        enable_automatic_payment_method=True,
    )
    credit_card_payment.status = "requires_capture"
    return credit_card_payment


class OrdersBase:
    async def create_order(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
        credit_card_payment: credit_card_models_pb2.CreditCardPayment,
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

        orders.send_booking_confirmation = mock.AsyncMock()

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
                                "id": credit_card_payment.id,
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


class TestOrders(OrdersBase):
    async def test_order_created(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
        credit_card_payment_client: credit_card_payment.Client,
    ) -> None:
        payment_intent = await pre_setup_credit_card(credit_card_payment_client)
        response = await self.create_order(
            authenticated_http_client,
            httpx_mock,
            payment_intent,
        )
        assert response.status_code == status.HTTP_201_CREATED

    async def test_get_order(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
        orders_repository: repository.OrdersRepository,
        credit_card_payment_client: credit_card_payment.Client,
    ) -> None:
        payment_intent = await pre_setup_credit_card(credit_card_payment_client)
        await self.create_order(
            authenticated_http_client,
            httpx_mock,
            payment_intent,
        )
        response = await authenticated_http_client.get(
            "/orders/{0}".format(_ORDER_ID),
        )

        assert response.json()["data"]["relationships"]["payment"]["data"]["id"]  # noqa: WPS219
        assert response.status_code == 200

    async def test_get_order_with_markup(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
        credit_card_payment_client: credit_card_payment.Client,
    ) -> None:
        payment_intent = await pre_setup_credit_card(credit_card_payment_client)
        await self.create_order(
            authenticated_http_client,
            httpx_mock,
            payment_intent,
        )
        await _create_markups(authenticated_http_client)

        response = await authenticated_http_client.get(
            "/orders/{0}".format(_ORDER_ID),
        )

        assert response.json()["data"]["relationships"]["markup"]["data"]["id"]  # noqa: WPS219
        assert response.status_code == 200

    async def test_get_user_orders(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
        orders_repository: repository.OrdersRepository,
        credit_card_payment_client: credit_card_payment.Client,
    ) -> None:
        payment_intent = await pre_setup_credit_card(credit_card_payment_client)
        await self.create_order(
            authenticated_http_client,
            httpx_mock,
            payment_intent,
        )
        response = await authenticated_http_client.get(
            "/orders",
        )

        assert response.json()["data"][0]["relationships"]["payment"]["data"]["id"]  # noqa: WPS219
        assert response.status_code == 200

    async def test_get_user_orders_with_markup(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
        credit_card_payment_client: credit_card_payment.Client,
    ) -> None:
        payment_intent = await pre_setup_credit_card(credit_card_payment_client)
        await self.create_order(
            authenticated_http_client,
            httpx_mock,
            payment_intent,
        )
        await _create_markups(authenticated_http_client)

        response = await authenticated_http_client.get(
            "/orders",
        )

        assert response.json()["data"][0]["relationships"]["markup"]["data"]["id"]  # noqa: WPS219
        assert response.status_code == 200

    async def test_create_cancellation_request(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
        credit_card_payment_client: credit_card_payment.Client,
    ) -> None:
        httpx_mock.add_response(
            **await conftest.load_response_fixture("GET_BOOKINGS_{ID}.json"),
        )
        httpx_mock.add_response(
            **await conftest.load_response_fixture("POST_CANCELLATIONS_REQUESTS.json"),
        )
        payment_intent = await pre_setup_credit_card(credit_card_payment_client)
        await self.create_order(
            authenticated_http_client,
            httpx_mock,
            payment_intent,
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
        credit_card_payment_client: credit_card_payment.Client,
    ) -> None:
        payment_intent = await pre_setup_credit_card(credit_card_payment_client)
        await self.create_order(authenticated_http_client, httpx_mock, payment_intent)

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
        credit_card_payment_client: credit_card_payment.Client,
    ) -> None:
        payment_intent = await pre_setup_credit_card(credit_card_payment_client)
        await self.create_order(authenticated_http_client, httpx_mock, payment_intent)

        await _create_markups(authenticated_http_client)

        response = await _create_markups(authenticated_http_client)

        assert response.status_code == 400

    async def test_get_markup_by_order(
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
        credit_card_payment_client: credit_card_payment.Client,
    ) -> None:
        payment_intent = await pre_setup_credit_card(credit_card_payment_client)
        await self.create_order(authenticated_http_client, httpx_mock, payment_intent)

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


class TestOrderByJourney(OrdersBase):
    async def test_create_order_by_journey(  # noqa: WPS217
        self,
        authenticated_http_client: httpx.AsyncClient,
        httpx_mock: pytest_httpx.HTTPXMock,
        monkeypatch: pytest.MonkeyPatch,
        orders_repository: repository.OrdersRepository,
        credit_card_payment_client: credit_card_payment.Client,
    ) -> None:
        payment_intent = await pre_setup_credit_card(credit_card_payment_client)
        response = await self.create_order(
            authenticated_http_client,
            httpx_mock,
            payment_intent,
        )
        httpx_mock.add_response(
            **await conftest.load_response_fixture("POST_ORDERS_BY_JOURNEY.json"),
        )
        journey = response.json()["data"]["relationships"]["journey"]
        payment_intent = await pre_setup_credit_card(credit_card_payment_client)

        journey_response = await authenticated_http_client.post(
            "/journeys/{0}/orders".format(journey["data"]["id"]),
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
                                "id": payment_intent.id,
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
        assert journey_response.status_code == status.HTTP_201_CREATED
        order_by_journey = await orders_repository.find_by_id(
            journey_response.json()["data"]["id"],
        )
        assert order_by_journey is not None


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
