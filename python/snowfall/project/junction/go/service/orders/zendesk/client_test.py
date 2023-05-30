import http

import more_itertools
import pytest
import pytest_httpx

from snowfall.project.junction.go.service.orders import orders
from snowfall.project.junction.go.service.orders.v1alpha import models_pb2
from snowfall.project.junction.go.service.orders.zendesk.client import ZendeskClient
from snowfall.stdlib.transport.http import errors


class TestZendeskClient(object):
    async def test_create_support_ticket(
        self,
        httpx_mock: pytest_httpx.HTTPXMock,
        zendesk_client: ZendeskClient,
        booking_repository: orders.BookingRepository,
        order: models_pb2.Order,
    ) -> None:
        booking_id = more_itertools.first(order.bookings).id
        booking = await booking_repository.find_by_id(booking_id)

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
        cancel_request_payload = zendesk_client.create_cancel_request_payload(
            booking,  # type: ignore[arg-type]
            order,
        )
        support_ticket_id = await zendesk_client.create_support_ticket(
            cancel_request_payload,
        )

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
