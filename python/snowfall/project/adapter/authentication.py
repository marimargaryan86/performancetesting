import abc

import grpc

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
from snowfall.stdlib import string
from snowfall.stdlib.jwt import JWTEncoder


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
    def __init__(
        self,
        private_key_content: str,
    ):
        self.email2user: dict[str, models_pb2.User] = {}
        self.id2user: dict[str, models_pb2.User] = {}
        self._jwt_encoder = JWTEncoder(private_key_content=private_key_content)

    async def authenticate(
        self,
        password: str,
        uuid: str = "",
        email: str = "",
    ) -> str:
        user = self._get_user(uuid, email)

        if not user:
            raise NotFoundError("User is not registered")

        if not match_passwords(password, user.password):
            raise InvalidArgumentError("Password is not correct")

        payload = {
            "email": user.email,
            "password": user.password,
            "id": user.id,
        }
        return self._jwt_encoder.encode(payload)

    async def create_user(  # noqa: WPS210
        self,
        email: str,
        password: str,
    ) -> models_pb2.User:
        email = email.lower()

        errors = []
        email_error = validate_email(email)
        if email_error:
            errors.append(email_error)
        password_error = validate_password(password)
        if password_error:
            errors.append(password_error)

        if errors:
            raise InvalidArgumentError("\n".join(errors))

        user = self._get_user(None, email)

        if user:
            raise AlreadyExistsError("User already exists")

        uuid = string.uuid()
        new_user = models_pb2.User(
            id=uuid,
            email=email,
            password=password2hash(password),
        )
        self.email2user[email] = new_user
        self.id2user[uuid] = new_user

        return new_user

    async def change_password(
        self,
        password: str,
        uuid: str = "",
        email: str = "",
    ) -> models_pb2.User:
        error = validate_password(password)
        if error:
            raise InvalidArgumentError(error)

        if email:
            email = email.lower()

        user = self._get_user(uuid, email)
        if not user:
            raise NotFoundError("User is not found")

        user.password = password2hash(password)

        return user

    def _get_user(
        self,
        uuid: str | None,
        email: str | None,
    ) -> models_pb2.User | None:
        user = None
        if uuid:
            user = self.id2user.get(uuid)

        if email and not user:
            user = self.email2user.get(email)

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
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(exc.details()) from exc

            if exc.code() == grpc.StatusCode.INVALID_ARGUMENT:
                raise InvalidArgumentError(exc.details()) from exc

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

        return response.user
