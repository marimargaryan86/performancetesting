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
            json={},
            headers={
                "Cirium-Flex-Alert-Key": cirium_flex_alert_key,
                "Cirium-Flex-Alert-Hash": cirium_flex_alert_hash,
            },
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
