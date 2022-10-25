from typing import Optional

import grpc

from snowfall.service.authentication import repository
from snowfall.service.authentication.v1alpha import authentication_pb2 as auth_pb2
from snowfall.service.authentication.v1alpha import (
    authentication_pb2_grpc as auth_pb2_grpc,
)
from snowfall.service.authentication.v1alpha import models_pb2
from snowfall.service.authentication.validators import (
    match_passwords,
    password2hash,
    validate_email,
    validate_password,
)
from snowfall.stdlib.jwt import JWTEncoder
from snowfall.stdlib.string import uuid
from snowfall.stdlib.transport.grpc import service


async def validate(
    email: str,
    password: str,
    context: grpc.aio.ServicerContext,
) -> None:
    email_error = validate_email(email)
    password_error = validate_password(password)
    if email_error or password_error:
        await context.abort(
            grpc.StatusCode.INVALID_ARGUMENT,
            details="\n".join([email_error, password_error]),
        )


class AuthenticationService(
    service.Service,
    auth_pb2_grpc.AuthenticationServiceServicer,
):
    def __init__(
        self,
        users: repository.UsersRepository,
        default_page_size: int,
        private_key_content: str,
    ):
        self._default_page_size: int = default_page_size
        self._users: repository.UsersRepository = users
        self._jwt_encoder: JWTEncoder = JWTEncoder(
            private_key_content=private_key_content,
        )

    def get_name(self) -> str:
        return auth_pb2.DESCRIPTOR.services_by_name["AuthenticationService"].full_name

    def register(
        self,
        server: grpc.aio.Server,
    ) -> None:
        auth_pb2_grpc.add_AuthenticationServiceServicer_to_server(self, server)

    async def Authenticate(  # type: ignore[override] # noqa: N802
        self,
        request: auth_pb2.AuthenticateRequest,
        context: grpc.aio.ServicerContext,
    ) -> Optional[auth_pb2.AuthenticateResponse]:
        if request.email:
            email = request.email.lower()

            user = await self._users.find_user_by_email(email)

        elif request.id:
            user = await self._users.find_user_by_id(request.id)

        if not user:
            return await context.abort(
                grpc.StatusCode.NOT_FOUND,
                details="User is not found",
            )

        if not match_passwords(request.password, user.password):
            return await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                details="Password is not correct",
            )

        payload = {
            "email": user.email,
            "password": user.password,
            "id": user.id,
        }
        token = self._jwt_encoder.encode(payload)

        return auth_pb2.AuthenticateResponse(auth_token=token)

    async def CreateUser(  # type: ignore[override] # noqa: N802
        self,
        request: auth_pb2.CreateUserRequest,
        context: grpc.aio.ServicerContext,
    ) -> Optional[auth_pb2.CreateUserResponse]:
        email = request.email.lower()

        await validate(email, request.password, context)

        user = await self._users.find_user_by_email(email)

        if user:
            return await context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                details="User is already exist",
            )

        hashed_password = password2hash(request.password)

        user = models_pb2.User(
            id=uuid(),
            email=email,
            password=hashed_password,
        )

        try:
            await self._users.insert(user)
        except RuntimeError:
            return await context.abort(
                grpc.StatusCode.ABORTED,
                details="User is not created",
            )

        context.set_code(grpc.StatusCode.OK)

        return auth_pb2.CreateUserResponse(user=user)

    async def ChangePassword(  # type: ignore[override, return] # noqa: N802, WPS217, C901
        self,
        request: auth_pb2.ChangePasswordRequest,
        context: grpc.ServicerContext,
    ) -> Optional[auth_pb2.ChangePasswordResponse]:
        error = validate_password(request.password)
        if error:
            return await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                details=error,
            )

        if request.email:
            email = request.email.lower()

            user = await self._users.find_user_by_email(email)

        elif request.id:
            user = await self._users.find_user_by_id(request.id)

        if not user:
            return await context.abort(
                grpc.StatusCode.NOT_FOUND,
                details="User is not found",
            )

        hashed_password = password2hash(request.password)
        updated_result = await self._users.update(
            user,
            hashed_password,
        )

        if updated_result.matched_count >= 1:
            # Need to reconsider matched_cout > 1 case
            user.password = hashed_password
            context.set_code(grpc.StatusCode.OK)
            return auth_pb2.ChangePasswordResponse(
                user=user,
            )

        if updated_result.matched_count == 0:
            return await context.abort(
                grpc.StatusCode.NOT_FOUND,
                details="Password is not changed",
            )
