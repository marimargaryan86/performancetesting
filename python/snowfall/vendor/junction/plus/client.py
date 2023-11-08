from snowfall.vendor.junction.client import BaseClient

_TYPE_KEY = "type"
_ATTRIBUTES_KEY = "attributes"


class Client(BaseClient):
    async def update_push_notification_token(
        self,
        token: str,
        mobile_phone: str,
    ) -> None:
        payload = {
            "data": {
                _TYPE_KEY: "push-notification-tokens",
                _ATTRIBUTES_KEY: {
                    "token": token,
                    "mobilePhone": mobile_phone,
                },
            },
        }

        response = await self._client.request(
            method="PATCH",
            url="/push-notifications/tokens",
            json=payload,
        )
        response.raise_for_status()
