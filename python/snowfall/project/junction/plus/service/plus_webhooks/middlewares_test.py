from collections.abc import Mapping

import httpx
from starlette import status


class TestCustomHeaderMiddleware(object):
    async def test_invalid_hmac(
        self,
        client: httpx.AsyncClient,
        cirium_flex_alert_key: str,
    ) -> None:
        response = await client.post(
            "/webhooks/alerts",
            json={},
            headers={
                "Cirium-Flex-Alert-Key": cirium_flex_alert_key,
                "Cirium-Flex-Alert-Hash": "wrong_hash",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

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
                    "flightStatus": {
                        "flightStatusUpdates": {
                            "flightStatusUpdate": [
                                {
                                    "updatedAt": {
                                        "dateUtc": "2023-07-18T08:07:13.848Z",
                                    },
                                    "source": "Simulated Event Source",
                                    "updatedDateFields": {
                                        "updatedDateField": [
                                            {
                                                "field": "EGD",
                                                "originalDateLocal": (
                                                    "2023-07-18T08:07:13.848"
                                                ),
                                                "newDateLocal": (
                                                    "2023-07-18T08:37:13.848"
                                                ),
                                            },
                                        ],
                                    },
                                    "updatedTextFields": {
                                        "updatedTextField": [
                                            {
                                                "field": "DGT",
                                                "originalText": "B3",
                                                "newText": "A4",
                                            },
                                        ],
                                    },
                                },
                            ],
                        },
                    },
                    "event": {
                        "type": "DEPARTURE_DELAY",
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

        assert response.status_code == status.HTTP_200_OK
