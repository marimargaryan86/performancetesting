from typing import Any

from snowfall.vendor.junction.client import BaseClient

_TYPE_KEY = "type"
_ATTRIBUTES_KEY = "attributes"


class Client(BaseClient):
    async def update_push_notification_token(
        self,
        token: str,
        mobile_phone: str,
    ) -> dict[str, Any]:
        payload = {
            "data": {
                _TYPE_KEY: "transactions",
                _ATTRIBUTES_KEY: {
                    "token": token,
                    "mobilePhone": mobile_phone,
                },
            },
        }

        return await self._make_request(
            method="PATCH",
            url="/push-notifications/tokens",
            payload=payload,
        )
