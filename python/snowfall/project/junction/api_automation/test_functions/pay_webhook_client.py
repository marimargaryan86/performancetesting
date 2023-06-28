import hashlib
import hmac
import json
import logging
from typing import Any

from snowfall.stdlib import string
from snowfall.vendor.junction.client import BaseClient

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def _count_hmac(message: str, secret_key: str) -> str:
    return hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha512,
    ).hexdigest()


class PayWebhookClient(BaseClient):  # noqa: WPS214
    async def trigger_payment_webhook(  # noqa: WPS211
        self,
        amount: str,
        beneficiary_id: str,
        currency_id: str,
        pay_date: str,
        reason: str,
        external_reference_id: str,
        status: str,
        pay_webhook_secret_key: str,
    ) -> dict[str, Any]:
        payload = {
            "header": {
                "message_type": "payment",
                "notification_type": "payment_released_notification",
            },
            "body": {
                "id": external_reference_id,
                "amount": amount,
                "failure_returned_amount": amount,
                "beneficiary_id": beneficiary_id,
                "conversion_id": string.uuid(),
                "currency": currency_id,
                "reference": "cc",
                "reason": reason,
                "status": status,
                "payment_type": "priority",
                "payment_date": pay_date,
                "transferred_at": pay_date,
                "authorisation_steps_required": "0",
                "creator_contact_id": string.uuid(),
                "last_updater_contact_id": string.uuid(),
                "short_reference": "180430-TSLCQJ001",
                "failure_reason": "Very dangerous failure",
                "payment_group_id": None,
                "unique_request_id": "Ciu4eNcYnq582hwK_8Cu47sk",
            },
        }

        content_body = json.dumps(payload)
        logger.info("webhook payload: %s", json.dumps(content_body, indent=4))

        calculated_hmac = _count_hmac(
            content_body,
            pay_webhook_secret_key,
        )
        response = await self._client.post(
            url="/webhooks/payments",
            json=payload,
            headers={
                "X-Hmac-Digest-Sha-512": calculated_hmac,
            },
        )
        response.raise_for_status()
        return response.json()
