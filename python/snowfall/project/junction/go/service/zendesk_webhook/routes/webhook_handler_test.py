from unittest import mock

import httpx
from starlette import status


async def test_webhook_event(
    client: httpx.AsyncClient,
    event_producer: mock.Mock,
) -> None:
    payload = {
        "ticket_id": "34936",
        "category": "Solved",
        "status": "No Refund",
    }

    response = await client.post(
        url="/zendesk_webhook",
        json=payload,
    )

    assert response.status_code == status.HTTP_200_OK
    event_producer.publish.assert_awaited()
    event = event_producer.publish.call_args[0][0]
    assert event.ticket_id == payload["ticket_id"]
    assert event.category == payload["category"]
    assert event.status == payload["status"]
