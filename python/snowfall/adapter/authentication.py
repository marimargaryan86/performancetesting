import abc
import dataclasses
import datetime
from collections.abc import Awaitable, Callable, Mapping

import asyncstdlib
import grpc

from snowfall.service.authentication.v1 import authentication_pb2 as auth_pb2
from snowfall.service.authentication.v1 import authentication_pb2_grpc as auth_pb2_grpc
from snowfall.service.authentication.v1 import models_pb2, oauth_pb2, oauth_pb2_grpc
from snowfall.stdlib import string
from snowfall.stdlib.format import jwt


class NotFoundError(Exception):
    """Raise when data is not found in mangodb."""


class InvalidArgumentError(Exception):
    """Raise when some arguments are not valid."""


class AlreadyExistsError(Exception):
    """Raise when the resource already exists."""


class Client(abc.ABC):
    @abc.abstractmethod
    async def authenticate(
        self,
        password: str,
        uuid: str = "",
        email: str = "",
    ) -> str:
        """Sign in into the system."""

    @abc.abstractmethod
    async def create_user(
        self,
        email: str,
        password: str,
    ) -> models_pb2.User:
        """Create a user in the system."""

    @abc.abstractmethod
    async def change_password(
        self,
        password: str,
        uuid: str = "",
        email: str = "",
    ) -> models_pb2.User:
        """Change a user password."""


class DictClient(Client):
    def __init__(self) -> None:
        self._email2user: dict[str, models_pb2.User] = {}
        self._id2user: dict[str, models_pb2.User] = {}
        self._encoder = jwt.Encoder()
        self._jwt_factory = JWTFactory(
            ttl=datetime.timedelta(hours=1),
        )

    async def authenticate(
        self,
        password: str,
        uuid: str = "",
        email: str = "",
    ) -> str:
        user = self._get_user(uuid, email)

        if not user or password != user.password:
            raise InvalidArgumentError("Password is not correct")

        return self._encoder.encode(self._jwt_factory.from_user(user))

    async def create_user(  # noqa: WPS210
        self,
        email: str,
        password: str,
    ) -> models_pb2.User:
        new_user = models_pb2.User(
            id=string.uuid(),
            email=email.lower(),
            password=password,
        )
        self._email2user[new_user.email] = new_user
        self._id2user[new_user.id] = new_user

        return new_user

    async def change_password(
        self,
        password: str,
        uuid: str = "",
        email: str = "",
    ) -> models_pb2.User:
        user = self._get_user(uuid, email.lower())

        if not user:
            raise NotFoundError("User is not found")

        user.password = password
        self._email2user[user.email] = user
        self._id2user[user.id] = user

        return user

    def _get_user(
        self,
        uuid: str | None,
        email: str | None,
    ) -> models_pb2.User | None:
        user = None
        if uuid:
            user = self._id2user.get(uuid)

        if email and not user:
            user = self._email2user.get(email)

        return user


class GrpcClient(Client):
    def __init__(
        self,
        authenticate: auth_pb2_grpc.AuthenticationServiceStub,
        timeout: int = 10,
    ):
        self._authenticate = authenticate
        self._timeout = timeout

    async def authenticate(
        self,
        password: str,
        uuid: str = "",
        email: str = "",
    ) -> str:
        try:
            response = await self._authenticate.Authenticate(
                auth_pb2.AuthenticateRequest(
                    **({"email": email} if email else {"id": uuid}),
                    password=password,
                ),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.INVALID_ARGUMENT:
                raise InvalidArgumentError(exc.details()) from exc

            raise

        return response.auth_token

    async def create_user(
        self,
        email: str,
        password: str,
    ) -> models_pb2.User:
        try:
            response = await self._authenticate.CreateUser(
                auth_pb2.CreateUserRequest(
                    email=email,
                    password=password,
                ),
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.INVALID_ARGUMENT:
                raise InvalidArgumentError(exc.details()) from exc

            if exc.code() == grpc.StatusCode.ALREADY_EXISTS:
                raise AlreadyExistsError(exc.details()) from exc

            raise

        return response.user

    async def change_password(
        self,
        password: str,
        uuid: str = "",
        email: str = "",
    ) -> models_pb2.User:
        try:
            response = await self._authenticate.ChangePassword(
                auth_pb2.ChangePasswordRequest(
                    **({"email": email} if email else {"id": uuid}),
                    password=password,
                ),
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.INVALID_ARGUMENT:
                raise InvalidArgumentError(exc.details()) from exc

            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(exc.details()) from exc

            raise

        return response.user


@dataclasses.dataclass(frozen=True)
class _UserInfo(object):
    id: str  # noqa: A003
    email: str
    metadata: Mapping[str, str] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(kw_only=True, frozen=True)
class _Version2Payload(jwt.Payload):
    user_info: _UserInfo
    version: str = dataclasses.field(default="2.0.0", init=False)


class JWTFactory(object):
    def __init__(
        self,
        ttl: datetime.timedelta,
    ):
        self._ttl = ttl

    def from_user(self, user: models_pb2.User) -> _Version2Payload:
        return _Version2Payload(
            user_info=_UserInfo(
                id=user.id,
                email=user.email,
                metadata=dict(user.metadata),
            ),
            exp=datetime.datetime.now(tz=datetime.UTC) + self._ttl,
            jti=string.uuid(),
        )


def get_jwk_url(authentication_address: str) -> str:
    authentication_channel = grpc.insecure_channel(authentication_address)
    oath_client = oauth_pb2_grpc.OAuthServiceStub(
        authentication_channel,
    )

    return oath_client.GetJWKUrl(oauth_pb2.GetJWKUrlRequest()).url


def oauth_client_resolver(
    oath_client: oauth_pb2_grpc.OAuthServiceStub,
) -> Callable[[str], Awaitable[str]]:
    @asyncstdlib.lru_cache()
    async def wrapper(client_id: str) -> str:
        response = await oath_client.GetClient(oauth_pb2.GetClientRequest(id=client_id))

        return response.owner

    return wrapper
