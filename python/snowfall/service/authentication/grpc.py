import grpc

from snowfall.service.authentication import auth, repository
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
from snowfall.stdlib.format import jwt
from snowfall.stdlib.string import uuid
from snowfall.stdlib.transport.grpc import rich_status, service


class AuthenticationService(
    service.Service,
    auth_pb2_grpc.AuthenticationServiceServicer,
):
    def __init__(
        self,
        users: repository.UsersRepository,
        jwt_factory: auth.JWTFactory,
        jwt_encoder: jwt.Encoder,
    ):
        self._users = users
        self._jwt_factory = jwt_factory
        self._jwt_encoder = jwt_encoder

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
    ) -> auth_pb2.AuthenticateResponse:
        if request.email:
            email = request.email.lower()

            user = await self._users.find_user_by_email(email)

        elif request.id:
            user = await self._users.find_user_by_id(request.id)

        if not user or not match_passwords(request.password, user.password):
            return await rich_status.abort_with_rich_status(
                context,
                rich_status.build_bad_request(
                    "password",
                    "Passwords do not match",
                    description="Passwords do not match",
                ),
            )

        payload = self._jwt_factory.from_user(user=user)

        return auth_pb2.AuthenticateResponse(
            auth_token=self._jwt_encoder.encode(payload),
        )

    async def CreateUser(  # type: ignore[override] # noqa: N802,WPS217
        self,
        request: auth_pb2.CreateUserRequest,
        context: grpc.aio.ServicerContext,
    ) -> auth_pb2.CreateUserResponse:
        email = request.email.lower()
        email_error = validate_email(email)
        if email_error:
            return await rich_status.abort_with_rich_status(
                context,
                rich_status.build_bad_request(
                    "email",
                    email_error,
                    description=email_error,
                ),
            )
        password_error = validate_password(request.password)
        if password_error:
            return await rich_status.abort_with_rich_status(
                context,
                rich_status.build_bad_request(
                    "password",
                    password_error,
                    description=password_error,
                ),
            )

        user = await self._users.find_user_by_email(email)

        if user:
            return await rich_status.abort_with_rich_status(
                context,
                rich_status.build_rich_status(
                    code=grpc.StatusCode.ALREADY_EXISTS,
                    error=rich_status.error_details_pb2.BadRequest(
                        field_violations=[
                            rich_status.error_details_pb2.BadRequest.FieldViolation(
                                field="user",
                                description="User already exists",
                            ),
                        ],
                    ),
                    description="User already exists",
                ),
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

    async def ChangePassword(  # type: ignore[override] # noqa: N802, WPS217, C901
        self,
        request: auth_pb2.ChangePasswordRequest,
        context: grpc.ServicerContext,
    ) -> auth_pb2.ChangePasswordResponse:
        error = validate_password(request.password)
        if error:
            return await rich_status.abort_with_rich_status(
                context,
                rich_status.build_bad_request("password", error, description=error),
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
            # Need to reconsider matched_count > 1 case
            user.password = hashed_password
            context.set_code(grpc.StatusCode.OK)
            return auth_pb2.ChangePasswordResponse(
                user=user,
            )

        return await context.abort(
            grpc.StatusCode.NOT_FOUND,
            details="Password is not changed",
        )
