from __future__ import annotations

import asyncio
import dataclasses
import datetime
import itertools
from collections.abc import AsyncIterable, Sequence
from typing import ClassVar, NamedTuple

from grpc import aio

from snowfall.project.junction.provider.v1alpha import (
    bookings_pb2_grpc,
    meta_pb2,
    meta_pb2_grpc,
    offers_pb2_grpc,
)
from snowfall.stdlib import sequence
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.grpc import client

_PROVIDER_REFRESH_RATE = datetime.timedelta(minutes=10)


class IdentifierAddressTuple(NamedTuple):
    identifier: str
    address: str


class IdentifierMismatchError(Exception):
    """Raised when a provider returns an identifier other than the configured one."""


class UnmarshalResult(NamedTuple):
    provider_id: str
    resource_id: str


@dataclasses.dataclass(frozen=False)  # noqa: SF10
class _ProviderWrapper(object):
    provider: Provider
    is_healthy: bool = False
    _lock: asyncio.Lock = dataclasses.field(default_factory=asyncio.Lock)
    _last_checked_at: datetime.datetime = dataclasses.field(
        default_factory=lambda: datetime.datetime.min.replace(tzinfo=datetime.UTC),
    )

    _logger: ClassVar[stdout.Logger] = stdout.get_logger()

    async def refresh(self) -> None:
        now = datetime.datetime.now(tz=datetime.UTC)

        if (now - self._last_checked_at) < _PROVIDER_REFRESH_RATE:
            return

        async with self._lock:
            # if _last_checked_at is later than our "now" timestamp,
            # another task has already refreshed this provider.
            if self._last_checked_at > now:
                return

            try:
                await self._do_refresh()
            except (aio.AioRpcError, IdentifierMismatchError):
                self.is_healthy = False  # noqa: WPS601
            else:
                self.is_healthy = True  # noqa: WPS601

            self._last_checked_at = datetime.datetime.now(  # noqa: WPS601
                tz=datetime.UTC,
            )
            self._logger.info(
                "Provider refreshed.",
                identifier=self.provider.identifier,
                name=self.provider.name,
                is_healthy=self.is_healthy,
            )

    async def _do_refresh(self) -> None:
        meta_response = await self.provider.connection.meta.GetIdentity(
            meta_pb2.GetIdentityRequest(),
        )

        if self.provider.identifier != meta_response.id:
            raise IdentifierMismatchError

        capabilities_response = await self.provider.connection.meta.GetCapabilities(
            meta_pb2.GetCapabilitiesRequest(),
        )

        self.provider = Provider(
            connection=self.provider.connection,
            identifier=meta_response.id,
            name=meta_response.name,
            trip_search_capabilities=capabilities_response.trip_search_capabilities,
        )


class Collection(object):
    def __init__(self, providers: Sequence[Provider]):
        self._providers = {
            provider.identifier: _ProviderWrapper(provider=provider)
            for provider in providers
        }

    async def find_by_id(self, identifier: str) -> Provider | None:
        try:
            provider = self._providers[identifier]
        except KeyError:
            return None

        await provider.refresh()

        if not provider.is_healthy:
            return None

        return provider.provider

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

    async def all_(self) -> AsyncIterable[Provider]:
        for provider in self._providers.values():
            await provider.refresh()

            if not provider.is_healthy:
                continue

            yield provider.provider


@dataclasses.dataclass(frozen=True)
class Provider(object):
    connection: Connection
    identifier: str
    name: str = ""
    trip_search_capabilities: meta_pb2.TripSearchCapabilities = dataclasses.field(
        default_factory=meta_pb2.TripSearchCapabilities,
    )

    def marshal_resource_id(self, resource_id: str) -> str:
        return sequence.to_composite_id([self.identifier, resource_id])


class Connection(object):
    def __init__(self, dsn: str):
        self._channel = client.create_channel(dsn)
        self._bookings = bookings_pb2_grpc.BookingServiceStub(self._channel)
        self._meta = meta_pb2_grpc.MetaServiceStub(self._channel)
        self._offers = offers_pb2_grpc.OfferServiceStub(self._channel)

    @property
    def bookings(self) -> bookings_pb2_grpc.BookingServiceStub:
        return self._bookings

    @property
    def meta(self) -> meta_pb2_grpc.MetaServiceStub:
        return self._meta

    @property
    def offers(self) -> offers_pb2_grpc.OfferServiceStub:
        return self._offers


def unmarshal_resource_id(resource_id: str) -> UnmarshalResult:
    parts = sequence.from_composite_id(resource_id)

    if len(parts) != 2:
        raise sequence.InvalidCompositeError

    return UnmarshalResult(parts[0], parts[1])


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
