import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.adapter import authentication
from snowfall.stdlib.integration.starlette import models, request_helpers

_DATA_KEY = "data"


class CreateUser(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        client: authentication.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        try:
            user = await client.create_user(body["email"], body["password"])
        except authentication.InvalidArgumentError as err:
            return models.JsonApiResponse(
                models.Body(
                    errors=[
                        models.Error(
                            status=str(status.HTTP_400_BAD_REQUEST),
                            code="bad_request",
                            detail=str(err),
                            source=models.ErrorSource(
                                pointer="/data/attributes",
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except authentication.AlreadyExistsError as err:
            return models.JsonApiResponse(
                models.Body(
                    errors=[
                        models.Error(
                            status=str(status.HTTP_403_FORBIDDEN),
                            code="forbidden",
                            detail=str(err),
                            source=models.ErrorSource(
                                pointer="/data/id",
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_403_FORBIDDEN,
            )

        payload = {
            _DATA_KEY: {
                "id": user.id,
                "type": "users",
                "attributes": {
                    "email": user.email,
                },
            },
        }

        return responses.JSONResponse(payload, status_code=status.HTTP_201_CREATED)


class Authenticate(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        client: authentication.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        try:
            auth_token = await client.authenticate(
                body["password"],
                email=body["email"],
            )
        except authentication.NotFoundError as err:
            return models.JsonApiResponse(
                models.Body(
                    errors=[
                        models.Error(
                            status=str(status.HTTP_404_NOT_FOUND),
                            code="not_found",
                            detail=str(err),
                            source=models.ErrorSource(
                                pointer="/data/attributes/email",
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except authentication.InvalidArgumentError as err:
            return models.JsonApiResponse(
                models.Body(
                    errors=[
                        models.Error(
                            status=str(status.HTTP_400_BAD_REQUEST),
                            code="bad_request",
                            detail=str(err),
                            source=models.ErrorSource(
                                pointer="/data/attributes",
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        payload = {
            _DATA_KEY: {
                "id": auth_token,
                "type": "user-tokens",
                "attributes": {
                    "token": auth_token,
                },
            },
        }

        return responses.JSONResponse(payload, status_code=status.HTTP_200_OK)


class ChangePassword(endpoints.HTTPEndpoint):
    async def patch(
        self,
        request: requests.Request,
        client: authentication.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        try:
            user = await client.change_password(
                body["password"],
                email=body.get("email", ""),
                uuid=request.user.username,
            )

        except authentication.InvalidArgumentError as err:
            return models.JsonApiResponse(
                models.Body(
                    errors=[
                        models.Error(
                            status=str(status.HTTP_400_BAD_REQUEST),
                            code="bad_request",
                            detail=str(err),
                            source=models.ErrorSource(
                                pointer="/data/attributes",
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except authentication.NotFoundError as err:
            return models.JsonApiResponse(
                models.Body(
                    errors=[
                        models.Error(
                            status=str(status.HTTP_404_NOT_FOUND),
                            code="not_found",
                            detail=str(err),
                            source=models.ErrorSource(
                                pointer="/data/attributes/email",
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_404_NOT_FOUND,
            )

        payload = {
            _DATA_KEY: {
                "id": user.id,
                "type": "users",
                "attributes": {
                    "email": user.email,
                },
            },
        }

        return responses.JSONResponse(payload, status_code=status.HTTP_200_OK)
