from __future__ import annotations

import asyncio
import base64
import dataclasses
import itertools
from collections.abc import Sequence
from typing import Iterable, NamedTuple

from snowfall.project.junction.provider.v1alpha import offers_pb2_grpc
from snowfall.stdlib.transport.grpc import client


class IdentifierAddressTuple(NamedTuple):
    identifier: str
    address: str


class Error(Exception):
    """Generic provider error."""


class UnavailableError(Error):
    """Raised when a provider is unavailable."""


class UnmarshalResult(NamedTuple):
    provider_id: str
    resource_id: str


class Collection(object):
    _lock: asyncio.Lock
    _providers: dict[str, Provider]

    def __init__(self, providers: Sequence[Provider]):
        self._lock = asyncio.Lock()
        self._providers = {provider.identifier: provider for provider in providers}

    def find_by_id(self, identifier: str) -> Provider | None:
        try:
            provider = self._providers[identifier]
        except KeyError:
            return None

        if not provider.is_healthy:
            return None

        return provider

    @classmethod
    async def from_identifier_address_tuples(
        cls,
        tuples: Sequence[IdentifierAddressTuple],
    ) -> Collection:
        return cls(
            [
                Provider(
                    connection=Connection(address),
                    identifier=identifier,
                )
                for identifier, address in tuples
            ],
        )

    def all_(self) -> Iterable[Provider]:
        yield from (
            provider for provider in self._providers.values() if provider.is_healthy
        )


@dataclasses.dataclass(frozen=True)
class Provider(object):
    connection: Connection
    identifier: str
    name: str = ""
    is_healthy: bool = True

    def marshal_resource_id(self, resource_id: str) -> str:
        raw = "\x00".join([self.identifier, resource_id])

        while len(raw) % 3 != 0:
            raw = "{0}\x00".format(raw)

        return base64.urlsafe_b64encode(raw.encode()).decode()


class Connection(object):
    def __init__(self, dsn: str):
        self._channel = client.create_channel(dsn)
        self._offers = offers_pb2_grpc.OfferServiceStub(self._channel)

    @property
    def offers(self) -> offers_pb2_grpc.OfferServiceStub:
        return self._offers


def unmarshal_resource_id(resource_id: str) -> UnmarshalResult:
    raw = base64.urlsafe_b64decode(resource_id).decode()
    provider_id, resource_id = raw.rstrip("\x00").split("\x00")

    return UnmarshalResult(provider_id, resource_id)


def unmarshal_resource_ids(resource_ids: Sequence[str]) -> dict[str, list[str]]:
    unmarshal_results = [
        unmarshal_resource_id(resource_id) for resource_id in resource_ids
    ]

    unmarshal_results.sort(key=lambda unmarshal_result: unmarshal_result.provider_id)

    return {
        group: [
            unmarshal_result.resource_id for unmarshal_result in group_unmarshal_results
        ]
        for group, group_unmarshal_results in itertools.groupby(
            unmarshal_results,
            key=lambda unmarshal_result: unmarshal_result.provider_id,
        )
    }
