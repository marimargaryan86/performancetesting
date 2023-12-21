import bcrypt
import email_validator
import grpc
import httpx
from google.protobuf import struct_pb2
from google.rpc import error_details_pb2

from snowfall.adapter import authentication
from snowfall.service.authentication import repository, sessions
from snowfall.service.authentication.v1 import (
    authentication_pb2 as auth_pb2,
)
from snowfall.service.authentication.v1 import authentication_pb2_grpc as auth_pb2_grpc
from snowfall.service.authentication.v1 import (
    identities_pb2,
    identities_pb2_grpc,
    models_pb2,
    oauth_pb2,
    oauth_pb2_grpc,
    sessions_pb2,
    sessions_pb2_grpc,
)
from snowfall.stdlib import string
from snowfall.stdlib.format import jwt
from snowfall.stdlib.transport.grpc import rich_status, service
from snowfall.vendor.ory import client, models


class AuthenticationService(
    service.Service,
    auth_pb2_grpc.AuthenticationServiceServicer,
):
    def __init__(
        self,
        users: repository.UsersRepository,
        jwt_factory: authentication.JWTFactory,
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
        user = None
        if request.email:
            email = request.email.lower()
            user = await self._users.find_user_by_email(email)
        elif request.id:
            user = await self._users.find_user_by_id(request.id)

        if not user or not _match_passwords(request.password, user.password):
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
        email_error = _validate_email(email)
        if email_error:
            return await rich_status.abort_with_rich_status(
                context,
                rich_status.build_bad_request(
                    "email",
                    email_error,
                    description=email_error,
                ),
            )
        password_error = _validate_password(request.password)
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
                    error=error_details_pb2.BadRequest(
                        field_violations=[
                            error_details_pb2.BadRequest.FieldViolation(
                                field="user",
                                description="User already exists",
                            ),
                        ],
                    ),
                    description="User already exists",
                ),
            )

        user = models_pb2.User(
            id=string.uuid(),
            email=email,
            password=bcrypt.hashpw(
                request.password.encode(),
                bcrypt.gensalt(),
            ).decode(),
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

    async def ChangePassword(  # type: ignore[override] # noqa: N802, WPS217
        self,
        request: auth_pb2.ChangePasswordRequest,
        context: grpc.ServicerContext,
    ) -> auth_pb2.ChangePasswordResponse:
        error = _validate_password(request.password)
        if error:
            return await rich_status.abort_with_rich_status(
                context,
                rich_status.build_bad_request("password", error, description=error),
            )

        user = None
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

        updated_result = await self._users.update(
            user,
            bcrypt.hashpw(request.password.encode(), bcrypt.gensalt()).decode(),
        )

        if updated_result.matched_count >= 1:
            context.set_code(grpc.StatusCode.OK)
            return auth_pb2.ChangePasswordResponse(
                user=user,
            )

        return await context.abort(
            grpc.StatusCode.NOT_FOUND,
            details="Password is not changed",
        )


class OAuthService(service.Service, oauth_pb2_grpc.OAuthServiceServicer):
    def __init__(self, ory_client: client.OryClient):
        self._client = ory_client

    def get_name(self) -> str:
        return oauth_pb2.DESCRIPTOR.services_by_name["OAuthService"].full_name

    def register(
        self,
        server: grpc.aio.Server,
    ) -> None:
        oauth_pb2_grpc.add_OAuthServiceServicer_to_server(self, server)

    async def GetClient(  # type: ignore[override] # noqa: N802
        self,
        request: oauth_pb2.GetClientRequest,
        context: grpc.aio.ServicerContext,
    ) -> oauth_pb2.GetClientResponse:
        try:
            oauth2_client = await self._client.get_client_by_id(request.id)
        except httpx.HTTPStatusError as err:
            if err.response.status_code == httpx.codes.NOT_FOUND.value:
                return await context.abort(grpc.StatusCode.NOT_FOUND)

            return await context.abort(grpc.StatusCode.UNKNOWN)

        return oauth_pb2.GetClientResponse(
            client=oauth_pb2.Client(
                id=oauth2_client.client_id,
                owner=oauth2_client.owner,
            ),
        )

    async def GetJWKUrl(  # type: ignore[override] # noqa: N802
        self,
        request: oauth_pb2.GetJWKUrlRequest,
        context: grpc.aio.ServicerContext,
    ) -> oauth_pb2.GetJWKUrlResponse:
        return oauth_pb2.GetJWKUrlResponse(
            url=self._client.jwk_url,
        )


def _match_passwords(
    password: str,
    password_hashed: str,
) -> bool:
    return bcrypt.checkpw(password.encode(), password_hashed.encode())


def _validate_password(password: str) -> str:
    if len(password) < 8:
        return "The password should be more than 8 characters"
    return ""


def _validate_email(email: str) -> str:
    try:
        email_validator.validate_email(email, check_deliverability=False)
    except email_validator.EmailSyntaxError as err:
        return str(err)
    return ""


class SessionService(service.Service, sessions_pb2_grpc.SessionServiceServicer):
    def __init__(self, sessions_client: sessions.Sessions):
        self._sessions = sessions_client

    def get_name(self) -> str:
        return sessions_pb2.DESCRIPTOR.services_by_name["SessionService"].full_name

    def register(
        self,
        server: grpc.aio.Server,
    ) -> None:
        sessions_pb2_grpc.add_SessionServiceServicer_to_server(self, server)

    async def GetSession(  # type: ignore[override] # noqa: N802
        self,
        request: sessions_pb2.GetSessionRequest,
        context: grpc.aio.ServicerContext,
    ) -> sessions_pb2.GetSessionResponse:
        try:
            session = await self._sessions.get_session_for_cookie(request.cookie)
        except sessions.NotFoundError:
            return await context.abort(grpc.StatusCode.NOT_FOUND)
        except sessions.UnknownError:
            return await context.abort(grpc.StatusCode.UNKNOWN)

        return sessions_pb2.GetSessionResponse(
            session=session,
        )


class IdentitiesService(
    service.Service,
    identities_pb2_grpc.IdentitiesServiceServicer,
):
    def __init__(self, ory_client: client.OryClient):
        self._client = ory_client

    def get_name(self) -> str:
        return identities_pb2.DESCRIPTOR.services_by_name["IdentitiesService"].full_name

    def register(
        self,
        server: grpc.aio.Server,
    ) -> None:
        identities_pb2_grpc.add_IdentitiesServiceServicer_to_server(self, server)

    async def GetIdentity(  # type: ignore[override] # noqa: N802
        self,
        request: identities_pb2.GetIdentityRequest,
        context: grpc.aio.ServicerContext,
    ) -> identities_pb2.GetIdentityResponse:
        try:
            identity = await self._client.get_identity(request.id)
        except httpx.HTTPStatusError as err:
            if err.response.status_code == httpx.codes.NOT_FOUND.value:
                return await context.abort(grpc.StatusCode.NOT_FOUND)

            return await context.abort(grpc.StatusCode.UNKNOWN)

        metadata_public = struct_pb2.Struct()
        metadata_public.update(identity.metadata_public)

        return identities_pb2.GetIdentityResponse(
            identity=identities_pb2.Identity(
                id=identity.identifier,
                email=identity.traits.email,
                metadata_public=metadata_public,
            ),
        )

    async def UpdateIdentity(  # type: ignore[override] # noqa: N802
        self,
        request: identities_pb2.UpdateIdentityRequest,
        context: grpc.aio.ServicerContext,
    ) -> identities_pb2.UpdateIdentityResponse:
        try:
            identity = await self._client.update_identity(
                identity=models.Identity(
                    id=request.identity.id,
                    traits=models.Traits(email=request.identity.email),
                    metadata_public=dict(request.identity.metadata_public.items()),
                ),
            )
        except httpx.HTTPStatusError as err:
            if err.response.status_code == httpx.codes.NOT_FOUND.value:
                return await context.abort(grpc.StatusCode.NOT_FOUND)

            return await context.abort(grpc.StatusCode.UNKNOWN)

        metadata_public = struct_pb2.Struct()
        metadata_public.update(identity.metadata_public)

        return identities_pb2.UpdateIdentityResponse(
            identity=identities_pb2.Identity(
                id=identity.identifier,
                email=identity.traits.email,
                metadata_public=metadata_public,
            ),
        )
