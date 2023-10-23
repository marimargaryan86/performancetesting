from unittest import mock

import httpx
from starlette import status


async def test_webhook_event_should_succeed(
    client: httpx.AsyncClient,
    event_producer: mock.Mock,
) -> None:
    payload = {
        "ticket_id": "34936",
        "category": "Solved",
        "status": "No Refund",
    }

    response = await client.post(
        headers={
            "x-zendesk-webhook-signature": (
                "F2MhOKqQRjuPbVTsJaGoM4vuvakyV3CxAvLrom0kzAk="
            ),
            "x-zendesk-webhook-signature-timestamp": "2023-10-19T08:10:00Z",
        },
        url="/zendesk_webhook",
        json=payload,
    )

    assert response.status_code == status.HTTP_200_OK
    event_producer.publish.assert_awaited()
    event = event_producer.publish.call_args[0][0]
    assert event.ticket_id == payload["ticket_id"]
    assert event.category == payload["category"]
    assert event.status == payload["status"]


async def test_webhook_event_should_fail(
    client: httpx.AsyncClient,
    event_producer: mock.Mock,
) -> None:
    response = await client.post(
        url="/zendesk_webhook",
        json={
            "ticket_id": "34936",
            "category": "Solved",
            "status": "No Refund",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    event_producer.publish.assert_not_awaited()
