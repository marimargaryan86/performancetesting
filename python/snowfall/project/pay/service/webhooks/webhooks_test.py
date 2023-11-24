import hashlib
import hmac
import json

import httpx
import pytest
from starlette import exceptions, status


def _count_hmac(message: str, secret_key: str) -> str:
    return hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha512,
    ).hexdigest()


class TestPaymentWebhooks(object):
    async def test_payment_webhooks(
        self,
        webhook_client: httpx.AsyncClient,
        secret_key: str,
        external_reference_id: str,
    ) -> None:
        payload = {
            "header": {
                "message_type": "payment",
                "notification_type": "payment_ready_to_send_notification",
            },
            "body": {
                "id": external_reference_id,
                "amount": "2000.00",
                "failure_returned_amount": "2000.00",
                "beneficiary_id": "509c6dd0-6b26-4fec-930f-937ddc428bba",
                "conversion_id": "e5e8c287-73c3-4998-a368-47937301e471",
                "currency": "GBP",
                "reference": "cc",
                "reason": "test",
                "status": "ready_to_send",
                "payment_type": "priority",
                "payment_date": "2022-02-02T00:00:00+00:00",
                "transferred_at": "2022-02-02T00:00:00+00:00",
                "authorisation_steps_required": "0",
                "creator_contact_id": "202b6291-99b4-0132-60c0-10b11cb33cfb",
                "last_updater_contact_id": "202b6291-99b4-0132-60c0-10b11cb33cfb",
                "short_reference": "180430-TSLCQJ001",
                "failure_reason": "Very dangerious failour",
                "payment_group_id": None,
                "unique_request_id": "Ciu4eNcYnq582hwK_8Cu47sk",
            },
        }
        content_body = json.dumps(payload)
        calculated_hmac = _count_hmac(content_body, secret_key)
        response = await webhook_client.post(
            "/cc/payments",
            json=payload,
            headers={
                "X-Hmac-Digest-Sha-512": calculated_hmac,
            },
        )

        assert response.status_code == status.HTTP_200_OK


class TestCustomHeaderMiddleware(object):
    async def test_without_hmac_header(
        self,
        webhook_client: httpx.AsyncClient,
    ) -> None:
        with pytest.raises(exceptions.HTTPException):
            (
                await webhook_client.post(
                    "/cc/payments",
                    json={},
                )
            ).raise_for_status()
