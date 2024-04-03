import http

import pytest
import pytest_httpx

from snowfall.stdlib.transport.http import errors
from snowfall.vendor.zendesk.client import ZendeskClient
from snowfall.vendor.zendesk.models import (
    cancellation_request as cancellation_request_models,
)


class TestZendeskClient:
    async def test_create_support_ticket(
        self,
        httpx_mock: pytest_httpx.HTTPXMock,
        zendesk_client: ZendeskClient,
    ) -> None:
        httpx_mock.add_response(
            url="https://test.api.com/api/v2/tickets",
            status_code=201,
            json={
                "ticket": {
                    "url": "https://test.api.com/api/v2/tickets/1.json",
                    "id": 1,
                    "created_at": "2023-05-04T17:03:59Z",
                    "updated_at": "2023-05-04T17:03:59Z",
                    "subject": "Support Ticket",
                    "raw_subject": "Support Ticket",
                    "description": "This is a new support ticket",
                    "status": "new",
                },
            },
        )

        support_ticket_id = await zendesk_client.create_support_ticket({})

        assert support_ticket_id == 1

    async def test_create_support_ticket_bad_request(
        self,
        httpx_mock: pytest_httpx.HTTPXMock,
        zendesk_client: ZendeskClient,
    ) -> None:
        status = http.HTTPStatus(http.HTTPStatus.BAD_REQUEST)
        httpx_mock.add_response(
            url="https://test.api.com/api/v2/tickets",
            status_code=status.value,
            json=[],
        )

        with pytest.raises(errors.HttpStatusError) as excinfo:
            await zendesk_client.create_support_ticket({})

        assert str(excinfo.value) == status.description  # noqa: WPS441

    async def test_create_cancel_request_payload(
        self,
        zendesk_client: ZendeskClient,
        booking: cancellation_request_models.Booking,
        order: cancellation_request_models.Order,
        journey: cancellation_request_models.Journey,
    ) -> None:
        cancel_request_payload = zendesk_client.create_cancel_request_payload(
            booking=booking,
            order=order,
            journey=journey,
            group_id=123,
        )

        assert cancel_request_payload

        payload_body = cancel_request_payload["ticket"]["comment"]["html_body"]

        assert payload_body
