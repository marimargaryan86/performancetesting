import copy
from typing import Mapping, Optional
from unittest import mock

import httpx
from starlette import status

from snowfall.project.junction.service.mobile_api import conftest, repository, smtp
from snowfall.project.junction.service.mobile_api.v1alpha import models_pb2

_VERIFICATION_CODE_URL = "/verification-code"
_USERS_URL = "/users"


async def _post_users(
    http_client: httpx.AsyncClient,
    headers: Mapping[str, str],
    user: models_pb2.User,
) -> httpx.Response:
    return await http_client.post(
        _USERS_URL,
        json={
            "data": {
                "type": "users",
                "attributes": {
                    "firstName": user.first_name,
                    "lastName": user.last_name,
                    "password": user.password,
                    "email": user.email,
                    "phone": user.phone.e164_number,
                },
            },
        },
        headers=dict(headers),
    )


class TestVerificationCode(object):
    async def test_verification_code_invalid_email(
        self,
        http_client: httpx.AsyncClient,
    ) -> None:
        response = await http_client.post(
            _VERIFICATION_CODE_URL,
            json={
                "data": {
                    "type": "verification-codes",
                    "id": "string",
                    "attributes": {"email": "notanemail"},
                },
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_verification_code_email_sent(
        self,
        http_client: httpx.AsyncClient,
        smtp_client: smtp.EmailClient,
        new_user: models_pb2.User,
    ) -> None:
        response = await http_client.post(
            _VERIFICATION_CODE_URL,
            json={
                "data": {
                    "type": "verification-codes",
                    "attributes": {"email": new_user.email},
                },
            },
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        smtp_client.send_email_notification.assert_called_once_with(  # type: ignore[attr-defined] # noqa: B950
            new_user.email,
            mock.ANY,
            mock.ANY,
        )

    async def test_verification_code_middleware(
        self,
        http_client: httpx.AsyncClient,
        headers: Mapping[str, str],
        new_user: models_pb2.User,
        new_user_verification_code: conftest.VerificationCode,
    ) -> None:
        # POST /users should be protected by OTP
        otp_headers = dict(copy.deepcopy(headers))
        otp_headers["Authorization"] = "Bearer {otp}".format(
            otp=new_user_verification_code.code,
        )
        assert (
            await _post_users(http_client, otp_headers, new_user)
        ).status_code == status.HTTP_204_NO_CONTENT

        otp_headers["Authorization"] = "Bearer {otp}".format(otp=None)
        assert (
            await _post_users(http_client, otp_headers, new_user)
        ).status_code == status.HTTP_401_UNAUTHORIZED

        otp_headers["Authorization"] = "Bearer {otp}".format(
            otp=new_user_verification_code.code[::-1],
        )
        assert (
            await _post_users(http_client, otp_headers, new_user)
        ).status_code == status.HTTP_401_UNAUTHORIZED


class TestUsers(object):
    async def test_user_created(
        self,
        http_client: httpx.AsyncClient,
        headers: Mapping[str, str],
        users_repository: repository.UsersRepository,
        new_user_verification_code: conftest.VerificationCode,
        new_user: models_pb2.User,
    ) -> None:
        otp_headers = dict(copy.deepcopy(headers))
        otp_headers["Authorization"] = "Bearer {otp}".format(
            otp=new_user_verification_code.code,
        )
        await http_client.post(
            _USERS_URL,
            json={
                "data": {
                    "type": "users",
                    "attributes": {
                        "firstName": new_user.first_name,
                        "lastName": new_user.last_name,
                        "password": new_user.password,
                        "email": new_user.email,
                        "phone": new_user.phone.e164_number,
                    },
                },
            },
            headers=otp_headers,
        )

        user = await users_repository.find_user_by_email(new_user.email)
        assert user is not None

    async def test_user_login(
        self,
        http_client: httpx.AsyncClient,
        existing_user: conftest.ExistingUser,
    ) -> None:
        assert (
            await self._post_sessions(
                http_client,
                existing_user["unhashed_password"],
                existing_user["model"],
            )
        ).status_code == status.HTTP_200_OK

        assert (
            await self._post_sessions(
                http_client,
                existing_user["unhashed_password"][::-1],
                existing_user["model"],
            )
        ).status_code == status.HTTP_401_UNAUTHORIZED

        assert (
            await self._post_sessions(http_client, None, existing_user["model"])
        ).status_code == status.HTTP_400_BAD_REQUEST

    async def test_jwt_middleware(
        self,
        http_client: httpx.AsyncClient,
        authenticated_http_client: httpx.AsyncClient,
    ) -> None:
        # GET /places should be a JWT protected route
        response = await http_client.get("/places")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = await authenticated_http_client.get("/places")

        assert response.status_code == status.HTTP_200_OK

    async def test_user_reset_password(
        self,
        http_client: httpx.AsyncClient,
        headers: Mapping[str, str],
        existing_user_verification_code: conftest.VerificationCode,
        existing_user: conftest.ExistingUser,
    ) -> None:
        otp_headers = dict(copy.deepcopy(headers))
        otp_headers["Authorization"] = "Bearer {otp}".format(
            otp=existing_user_verification_code.code,
        )
        assert (
            await self._patch_user(
                http_client,
                existing_user["model"].email,
                existing_user,
                otp_headers,
            )
        ).status_code == status.HTTP_204_NO_CONTENT
        assert (
            await self._patch_user(http_client, None, existing_user, otp_headers)
        ).status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            await self._patch_user(
                http_client,
                existing_user["model"].email[::-1],
                existing_user,
                otp_headers,
            )
        ).status_code == status.HTTP_401_UNAUTHORIZED

    async def _post_sessions(
        self,
        http_client: httpx.AsyncClient,
        password: Optional[str],
        user: models_pb2.User,
    ) -> httpx.Response:
        return await http_client.post(
            "{base}/sessions".format(base=_USERS_URL),
            json={
                "data": {
                    "type": "user-sessions",
                    "attributes": {
                        "password": password,
                        "email": user.email,
                    },
                },
            },
        )

    async def _patch_user(
        self,
        http_client: httpx.AsyncClient,
        email: Optional[str],
        user: conftest.ExistingUser,
        headers: Mapping[str, str],
    ) -> httpx.Response:
        return await http_client.patch(
            "{base}/{email}".format(base=_USERS_URL, email=email),
            json={
                "data": {
                    "type": "users",
                    "id": user["model"].id,
                    "attributes": {
                        "password": user["unhashed_password"][::-1],
                    },
                },
            },
            headers=dict(headers),
        )
