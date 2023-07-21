from collections.abc import Mapping

import httpx
import pytest
from starlette import exceptions, status


class TestCustomHeaderMiddleware(object):
    async def test_invalid_hmac(
        self,
        client: httpx.AsyncClient,
        cirium_flex_alert_key: str,
    ) -> None:
        with pytest.raises(exceptions.HTTPException):
            await client.post(
                "/webhooks/alerts",
                json={},
                headers={
                    "Cirium-Flex-Alert-Key": cirium_flex_alert_key,
                    "Cirium-Flex-Alert-Hash": "wrong_hash",
                },
            )

    async def test_valid_hmac(
        self,
        client: httpx.AsyncClient,
        cirium_flex_alert_key: str,
        cirium_flex_alert_hash: str,
    ) -> None:
        response = await client.post(
            "/webhooks/alerts",
            json={
                "alert": {
                    "rule": {
                        "nameValues": {
                            "nameValue": [
                                {
                                    "name": "resource_id",
                                    "value": "monitoring_rule_1",
                                },
                            ],
                        },
                    },
                },
            },
            headers={
                "Cirium-Flex-Alert-Key": cirium_flex_alert_key,
                "Cirium-Flex-Alert-Hash": cirium_flex_alert_hash,
            },
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestWhatsappMiddleware(object):
    async def test_valid_hmac(
        self,
        client: httpx.AsyncClient,
        whatsapp_body: Mapping[str, str],
        whatsapp_body_hash: str,
    ) -> None:
        response = await client.post(
            url="/webhooks/whatsapp",
            data=whatsapp_body,
            headers={
                "content-type": "application/x-www-form-urlencoded",
                "x-twilio-signature": whatsapp_body_hash,
            },
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
