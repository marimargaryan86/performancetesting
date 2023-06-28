import lagom
from pymongo.errors import DuplicateKeyError
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.extensions.service.mobile_api import (
    repository,
    resources,
)
from snowfall.project.junction.extensions.service.mobile_api.v1alpha import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.integration.starlette import models, request_helpers


class PushNotificationTokens(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        notification_tokens_repository: repository.NotificationTokensRepository = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        try:
            token = await notification_tokens_repository.insert(
                models_pb2.NotificationToken(
                    id=string.uuid(),
                    notification_token=body["notificationToken"],
                    user_id=request.user.username,
                    device_token=body["deviceToken"],
                ),
            )
        except DuplicateKeyError:
            return models.JsonApiResponse(
                models.Body(
                    errors=[
                        models.Error(
                            status=str(status.HTTP_400_BAD_REQUEST),
                            code="duplicated_error",
                            detail="You can register each token and device only once",
                        ),
                    ],
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return models.JsonApiResponse(
            models.Body(
                data=resources.PushNotificationToken.from_proto(token),
            ),
            status.HTTP_201_CREATED,
        )

    async def get(
        self,
        request: requests.Request,
        notification_tokens_repository: repository.NotificationTokensRepository = lagom.injectable,
    ) -> responses.Response:
        tokens = await notification_tokens_repository.find_by_user(
            request.user.username,
        )
        try:
            first_token = resources.PushNotificationToken.from_proto(
                await tokens.take(),
            )
        except StopAsyncIteration as exc:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from exc

        return models.JsonApiResponse(
            models.Body(
                data=[first_token]
                + [
                    resources.PushNotificationToken.from_proto(token)
                    async for token in tokens
                ],
            ),
        )


class PushNotificationToken(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        notification_tokens_repository: repository.NotificationTokensRepository = lagom.injectable,
    ) -> responses.Response:
        token = await notification_tokens_repository.find_by_id(
            request.path_params["deviceToken"],
            "device_token",
        )
        if not token or token.user_id != request.user.username:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)
        return models.JsonApiResponse(
            models.Body(
                data=resources.PushNotificationToken.from_proto(token),
            ),
        )

    async def patch(
        self,
        request: requests.Request,
        notification_tokens_repository: repository.NotificationTokensRepository = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        update_result = await notification_tokens_repository.refresh_token(
            request.user.username,
            request.path_params["deviceToken"],
            body["notificationToken"],
        )
        if not update_result.matched_count:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)
        token = await notification_tokens_repository.find_by_id(
            request.path_params["deviceToken"],
            "device_token",
        )
        if not token or token.user_id != request.user.username:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)
        return models.JsonApiResponse(
            models.Body(
                data=resources.PushNotificationToken.from_proto(token),
            ),
        )

    async def delete(
        self,
        request: requests.Request,
        notification_tokens_repository: repository.NotificationTokensRepository = lagom.injectable,
    ) -> responses.Response:
        device_id = request.path_params["deviceToken"]
        deleted_count = await notification_tokens_repository.delete(
            device_id,
            request.user.username,
        )
        if not deleted_count:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)
        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)
