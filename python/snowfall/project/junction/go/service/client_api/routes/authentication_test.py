import httpx
from starlette import status

from snowfall.service.authentication.v1alpha import models_pb2 as auth_models_pb2


class TestAuth(object):
    async def test_auth_success(
        self,
        unauthorized_client: httpx.AsyncClient,
        user: auth_models_pb2.User,
    ) -> None:
        response = await unauthorized_client.post(
            "/users/tokens",
            json={
                "data": {
                    "attributes": {
                        "email": user.email,
                        "password": "myPassword",
                    },
                    "type": "user-tokens",
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_200_OK

    async def test_auth_unregistered_user(
        self,
        unauthorized_client: httpx.AsyncClient,
    ) -> None:
        response = await unauthorized_client.post(
            "/users/tokens",
            json={
                "data": {
                    "attributes": {
                        "email": "unregistered@example.com",
                        "password": "myPassword",
                    },
                    "type": "user-tokens",
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_auth_incorrect_password(
        self,
        unauthorized_client: httpx.AsyncClient,
        user: auth_models_pb2.User,
    ) -> None:
        response = await unauthorized_client.post(
            "/users/tokens",
            json={
                "data": {
                    "attributes": {
                        "email": user.email,
                        "password": "wrongPassword",
                    },
                    "type": "user-tokens",
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
