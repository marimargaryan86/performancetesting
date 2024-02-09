from collections.abc import Mapping
from types import MappingProxyType
from unittest import mock

import grpc
import pytest
from google.protobuf import struct_pb2

from snowfall.adapter import identities
from snowfall.service.authentication.v1 import (
    identities_pb2,
    identities_pb2_grpc,
)

NOT_FOUND = "924de040-3c88-4d4f-b909-acbe45753b05"
IDENTITIES = (
    "2a02cada-8274-4281-8d97-cbf3909a99bb",
    "b6b581cf-8601-4d5f-85dd-38cc111c4f6e",
)
METADATA_PUBLIC = MappingProxyType(
    {
        "role": "reseller-admin",
        "reseller_id": "mock",
    },
)
USER_EMAIL = "foobar@example.com"


@pytest.fixture()
def identities_client() -> identities.Client:
    return identities.DictClient(_get_identities())


@pytest.fixture()
def updated_metadata() -> dict[str, str]:
    new_metadata = METADATA_PUBLIC.copy()
    new_metadata["some_new_field_name"] = "some_new_value"

    return new_metadata


@pytest.fixture()
def error_stub() -> identities_pb2_grpc.IdentitiesServiceStub:
    error = grpc.aio.AioRpcError(
        code=grpc.StatusCode.NOT_FOUND,
        initial_metadata=grpc.aio.Metadata(),
        trailing_metadata=grpc.aio.Metadata(),
    )
    stub = mock.create_autospec(identities_pb2_grpc.IdentitiesServiceStub)
    stub.GetIdentity = mock.AsyncMock(side_effect=error)
    stub.UpdateIdentity = mock.AsyncMock(side_effect=error)
    stub.ListIdentities = mock.AsyncMock(side_effect=error)

    return stub


@pytest.fixture()
def invalid_args_stub() -> identities_pb2_grpc.IdentitiesServiceStub:
    error = grpc.aio.AioRpcError(
        code=grpc.StatusCode.INVALID_ARGUMENT,
        initial_metadata=grpc.aio.Metadata(),
        trailing_metadata=grpc.aio.Metadata(),
    )
    stub = mock.create_autospec(identities_pb2_grpc.IdentitiesServiceStub)
    stub.CreateIdentity = mock.AsyncMock(side_effect=error)

    return stub


@pytest.fixture()
def already_exists_stub() -> identities_pb2_grpc.IdentitiesServiceStub:
    error = grpc.aio.AioRpcError(
        code=grpc.StatusCode.ALREADY_EXISTS,
        initial_metadata=grpc.aio.Metadata(),
        trailing_metadata=grpc.aio.Metadata(),
    )
    stub = mock.create_autospec(identities_pb2_grpc.IdentitiesServiceStub)
    stub.CreateIdentity = mock.AsyncMock(side_effect=error)

    return stub


@pytest.fixture()
def stub(
    updated_metadata: Mapping[str, str],
) -> identities_pb2_grpc.IdentitiesServiceStub:
    identity = _get_identities()[0]
    get_identity_response = identities_pb2.GetIdentityResponse(
        identity=identity,
    )

    create_identity_response = identities_pb2.CreateIdentityResponse(
        identity=identity,
    )

    identity.metadata_public.update(updated_metadata)
    update_identity_response = identities_pb2.UpdateIdentityResponse(
        identity=identity,
    )

    list_identities_response = identities_pb2.ListIdentitiesResponse(
        identities=_get_identities(),
    )

    stub = mock.create_autospec(identities_pb2_grpc.IdentitiesServiceStub)
    stub.GetIdentity = mock.AsyncMock(return_value=get_identity_response)
    stub.CreateIdentity = mock.AsyncMock(return_value=create_identity_response)
    stub.UpdateIdentity = mock.AsyncMock(return_value=update_identity_response)
    stub.ListIdentities = mock.AsyncMock(return_value=list_identities_response)
    stub.DeleteIdentity = mock.AsyncMock(return_value=None)

    return stub


class TestDictClient(object):
    async def test_identity_is_retrievable(
        self,
        identities_client: identities.Client,
    ) -> None:
        identity = await identities_client.get_ory_identity(IDENTITIES[0])

        assert identity.id == IDENTITIES[0]

    async def test_identity_not_found(
        self,
        identities_client: identities.Client,
    ) -> None:
        with pytest.raises(identities.NotFoundError):
            await identities_client.get_ory_identity(NOT_FOUND)

    async def test_create_identity(
        self,
        identities_client: identities.Client,
    ) -> None:
        identity = _get_identities()[0]
        identity = await identities_client.create_ory_identity(
            email=identity.email,
            metadata=dict(identity.metadata_public),
        )

        assert identity.email == USER_EMAIL
        assert dict(identity.metadata_public.items()) == METADATA_PUBLIC

    async def test_create_identity_failure(
        self,
        identities_client: identities.Client,
    ) -> None:
        with pytest.raises(identities.InvalidArgumentError):
            await identities_client.create_ory_identity(
                email="",
                metadata={},
            )

    async def test_update_identity(
        self,
        identities_client: identities.Client,
        updated_metadata: Mapping[str, str],
    ) -> None:
        identity = _get_identities()[0]

        identity = await identities_client.update_ory_identity(
            identifier=identity.id,
            email=USER_EMAIL,
            metadata=updated_metadata,
        )

        assert identity.id == IDENTITIES[0]
        assert identity.email == USER_EMAIL
        assert dict(identity.metadata_public.items()) == updated_metadata

    async def test_update_identity_not_found(
        self,
        identities_client: identities.Client,
    ) -> None:
        with pytest.raises(identities.NotFoundError):
            await identities_client.update_ory_identity(
                identifier=NOT_FOUND,
                email="",
                metadata={},
            )

    async def test_list_identities(
        self,
        identities_client: identities.Client,
    ) -> None:
        identities_response = await identities_client.list_ory_identities()

        assert len(identities_response.identities) == 2

    async def test_list_identities_by_ids(
        self,
        identities_client: identities.Client,
    ) -> None:
        identities_response = await identities_client.list_ory_identities(
            identifiers=[IDENTITIES[0]],
        )

        assert len(identities_response.identities) == 1

    async def test_delete_identity(
        self,
        identities_client: identities.Client,
    ) -> None:
        identities = await identities_client.list_ory_identities()
        assert len(identities.identities) == 2

        first_identity = next(iter(identities.identities))
        await identities_client.delete_ory_identity(identifier=first_identity.id)

        identities = await identities_client.list_ory_identities()
        assert len(identities.identities) == 1


class TestGrpcClient(object):
    async def test_identity_is_retrievable(
        self,
        stub: identities_pb2_grpc.IdentitiesServiceStub,
    ) -> None:
        identities_client = identities.GrpcClient(stub)

        identity = await identities_client.get_ory_identity(IDENTITIES[0])

        assert identity.id == IDENTITIES[0]

    async def test_identity_is_retrievable_not_found(
        self,
        error_stub: identities_pb2_grpc.IdentitiesServiceStub,
    ) -> None:
        identities_client = identities.GrpcClient(error_stub)

        with pytest.raises(identities.NotFoundError):
            await identities_client.get_ory_identity(NOT_FOUND)

    async def test_create_ory_identity(
        self,
        stub: identities_pb2_grpc.IdentitiesServiceStub,
    ) -> None:
        identities_client = identities.GrpcClient(stub)

        identity = await identities_client.create_ory_identity(
            email="it does not matter",
            metadata={"role": "what I put here"},
        )

        assert identity.id == IDENTITIES[0]
        assert identity.email == USER_EMAIL
        assert dict(identity.metadata_public.items()) == METADATA_PUBLIC

    async def test_create_ory_identity_invalid_arguments(
        self,
        invalid_args_stub: identities_pb2_grpc.IdentitiesServiceStub,
    ) -> None:
        identities_client = identities.GrpcClient(invalid_args_stub)
        with pytest.raises(identities.InvalidArgumentError):
            await identities_client.create_ory_identity(
                email="",
                metadata={},
            )

    async def test_create_ory_identity_already_exists(
        self,
        already_exists_stub: identities_pb2_grpc.IdentitiesServiceStub,
    ) -> None:
        identities_client = identities.GrpcClient(already_exists_stub)
        with pytest.raises(identities.AlreadyExistsError):
            await identities_client.create_ory_identity(
                email="",
                metadata={},
            )

    async def test_update_identity(
        self,
        stub: identities_pb2_grpc.IdentitiesServiceStub,
        updated_metadata: Mapping[str, str],
    ) -> None:
        identities_client = identities.GrpcClient(stub)

        identity = _get_identities()[0]
        identity = await identities_client.update_ory_identity(
            identifier=identity.id,
            email=USER_EMAIL,
            metadata=updated_metadata,
        )

        assert identity.email == USER_EMAIL
        assert identity.id == IDENTITIES[0]
        assert dict(identity.metadata_public.items()) == updated_metadata

    async def test_update_identity_not_found(
        self,
        error_stub: identities_pb2_grpc.IdentitiesServiceStub,
    ) -> None:
        identities_client = identities.GrpcClient(error_stub)

        with pytest.raises(identities.NotFoundError):
            await identities_client.update_ory_identity(
                identifier=NOT_FOUND,
                email="",
                metadata={},
            )

    async def test_list_identities(
        self,
        stub: identities_pb2_grpc.IdentitiesServiceStub,
    ) -> None:
        identities_client = identities.GrpcClient(stub)

        identities_response = await identities_client.list_ory_identities()

        assert len(identities_response.identities) == 2


def _get_identities() -> list[identities_pb2.Identity]:
    return [_generate_identities(identifier) for identifier in IDENTITIES]


def _generate_identities(identifier: str) -> identities_pb2.Identity:
    metadata_public = struct_pb2.Struct()
    metadata_public.update(METADATA_PUBLIC)
    return identities_pb2.Identity(
        id=identifier,
        email=USER_EMAIL,
        metadata_public=metadata_public,
    )
