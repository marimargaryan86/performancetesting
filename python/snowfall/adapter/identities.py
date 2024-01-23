import abc
from collections.abc import Mapping, Sequence
from typing import Any

import grpc
from google.protobuf import struct_pb2

from snowfall.service.authentication.v1 import (
    identities_pb2,
    identities_pb2_grpc,
)
from snowfall.stdlib import string


class NotFoundError(Exception):
    """Raise when the ORY user is not found for the provided identifier."""


class InvalidArgumentError(Exception):
    """Raise when ORY user creation fails for the provided payload."""


class AlreadyExistsError(Exception):
    """Raise when ORY user creation fails because the identity already exists."""


class Client(abc.ABC):
    @abc.abstractmethod
    async def get_ory_identity(
        self,
        identifier: str,
    ) -> identities_pb2.Identity:
        """Get an ORY identity."""

    @abc.abstractmethod
    async def create_ory_identity(
        self,
        email: str,
        metadata: Mapping[str, Any],
    ) -> identities_pb2.Identity:
        """Create an ORY identity."""

    @abc.abstractmethod
    async def update_ory_identity(
        self,
        identifier: str,
        email: str,
        metadata: Mapping[str, Any],
    ) -> identities_pb2.Identity:
        """Update an ORY identity."""


class DictClient(Client):
    def __init__(
        self,
        identities: Sequence[identities_pb2.Identity],
    ) -> None:
        self._identities = {identity.id: identity for identity in identities}

    async def get_ory_identity(
        self,
        identifier: str,
    ) -> identities_pb2.Identity:
        identity = self._identities.get(identifier)

        if not identity:
            raise NotFoundError()

        return identity

    async def create_ory_identity(
        self,
        email: str,
        metadata: Mapping[str, Any],
    ) -> identities_pb2.Identity:
        metadata_public = struct_pb2.Struct()
        metadata_public.update(metadata)

        identity = identities_pb2.Identity(
            id=string.uuid(),
            email=email.lower(),
            metadata_public=metadata_public,
        )

        if not identity.email or not identity.metadata_public:
            raise InvalidArgumentError()

        return identity

    async def update_ory_identity(
        self,
        identifier: str,
        email: str,
        metadata: Mapping[str, Any],
    ) -> identities_pb2.Identity:
        identity = self._identities.get(identifier)

        if not identity:
            raise NotFoundError()

        identity.metadata_public.update(metadata)

        return identity


class GrpcClient(Client):
    def __init__(
        self,
        identity_service: identities_pb2_grpc.IdentitiesServiceStub,
        timeout: int = 10,
    ):
        self._identity_service = identity_service
        self._timeout = timeout

    async def get_ory_identity(
        self,
        identifier: str,
    ) -> identities_pb2.Identity:
        try:
            response = await self._identity_service.GetIdentity(
                identities_pb2.GetIdentityRequest(
                    id=identifier,
                ),
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(exc.details()) from exc

            raise

        return response.identity

    async def create_ory_identity(
        self,
        email: str,
        metadata: Mapping[str, Any],
    ) -> identities_pb2.Identity:
        metadata_public = struct_pb2.Struct()
        metadata_public.update(metadata)

        try:
            response = await self._identity_service.CreateIdentity(
                identities_pb2.CreateIdentityRequest(
                    identity=identities_pb2.Identity(
                        email=email,
                        metadata_public=metadata_public,
                    ),
                ),
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.INVALID_ARGUMENT:
                raise InvalidArgumentError(exc.details()) from exc
            if exc.code() == grpc.StatusCode.ALREADY_EXISTS:
                raise AlreadyExistsError(exc.details()) from exc

            raise

        return response.identity

    async def update_ory_identity(
        self,
        identifier: str,
        email: str,
        metadata: Mapping[str, Any],
    ) -> identities_pb2.Identity:
        metadata_public = struct_pb2.Struct()
        metadata_public.update(metadata)

        try:
            response = await self._identity_service.UpdateIdentity(
                identities_pb2.UpdateIdentityRequest(
                    identity=identities_pb2.Identity(
                        id=identifier,
                        email=email,
                        metadata_public=metadata_public,
                    ),
                ),
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(exc.details()) from exc

            raise

        return response.identity
