import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.plus.adapter import (
    subscribers,
)
from snowfall.stdlib.integration.starlette import request_helpers


class Tokens(endpoints.HTTPEndpoint):
    async def patch(
        self,
        request: requests.Request,
        subscribers_client: subscribers.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        reseller_id = request.user.username

        update_response = await subscribers_client.update_notification_token(
            reseller_id=reseller_id,
            mobile_phone=body.get("mobile_phone", ""),
            token=body.get("token", ""),
        )
        if update_response:
            return responses.Response(status_code=status.HTTP_204_NO_CONTENT)
        raise exceptions.HTTPException(status.HTTP_400_BAD_REQUEST)
