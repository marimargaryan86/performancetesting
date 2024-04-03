from __future__ import annotations

import asyncio
import dataclasses
import datetime
import itertools
from collections.abc import AsyncIterable, Sequence
from typing import ClassVar, NamedTuple

import prometheus_client
from grpc import aio

from snowfall.project.junction.rocket.provider.v1alpha import (
    bookings_pb2_grpc,
    meta_pb2,
    meta_pb2_grpc,
    searches_pb2_grpc,
)
from snowfall.stdlib import sequence
from snowfall.stdlib.logging import stdout

_PROVIDER_REFRESH_RATE = datetime.timedelta(minutes=10)


class IdentifierChannelTuple(NamedTuple):
    identifier: str
    channel: aio.Channel


class IdentifierMismatchError(Exception):
    """Raised when a provider returns an identifier other than the configured one."""


class UnmarshalResult(NamedTuple):
    provider_id: str
    resource_id: str


@dataclasses.dataclass(frozen=False)  # noqa: SF10
class _ProviderWrapper:
    provider: Provider
    is_healthy: bool = False
    _lock: asyncio.Lock = dataclasses.field(default_factory=asyncio.Lock)
    _last_checked_at: datetime.datetime = dataclasses.field(
        default_factory=lambda: datetime.datetime.min.replace(tzinfo=datetime.UTC),
    )

    _logger: ClassVar[stdout.Logger] = stdout.get_logger()
    _provider_status = prometheus_client.Enum(
        "gateway_provider_status",
        "The current status of a provider",
        ["provider_id"],
        states=["healthy", "unhealthy"],
    )

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
                self._provider_status.labels(
                    provider_id=self.provider.identifier,
                ).state("unhealthy")
                self.is_healthy = False  # noqa: WPS601
            else:
                self._provider_status.labels(
                    provider_id=self.provider.identifier,
                ).state("healthy")
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
            booking_capabilities=capabilities_response.booking_capabilities,
        )


class Collection:
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
    async def from_identifier_channel_tuples(
        cls,
        tuples: Sequence[IdentifierChannelTuple],
    ) -> Collection:
        return cls(
            [
                Provider(
                    connection=Connection(channel),
                    identifier=identifier,
                )
                for identifier, channel in tuples
            ],
        )

    def is_healthy(self, identifier: str) -> bool:
        try:
            return self._providers[identifier].is_healthy
        except KeyError as err:
            raise ValueError("Unknown identifier") from err

    async def all_(self) -> AsyncIterable[Provider]:
        for provider in self._providers.values():
            await provider.refresh()

            yield provider.provider

    async def all_healthy(self) -> AsyncIterable[Provider]:
        for provider in self._providers.values():
            await provider.refresh()

            if not provider.is_healthy:
                continue

            yield provider.provider


@dataclasses.dataclass(frozen=True)
class Provider:
    connection: Connection
    identifier: str
    name: str = ""
    booking_capabilities: meta_pb2.BookingCapabilities = dataclasses.field(
        default_factory=meta_pb2.BookingCapabilities,
    )

    def marshal_resource_id(self, resource_id: str) -> str:
        return sequence.to_composite_id([self.identifier, resource_id])


class Connection:
    def __init__(self, channel: aio.Channel):
        self._channel = channel
        self._bookings = bookings_pb2_grpc.BookingServiceStub(self._channel)
        self._meta = meta_pb2_grpc.MetaServiceStub(self._channel)
        self._searches = searches_pb2_grpc.SearchServiceStub(self._channel)

    @property
    def bookings(self) -> bookings_pb2_grpc.BookingServiceStub:
        return self._bookings

    @property
    def meta(self) -> meta_pb2_grpc.MetaServiceStub:
        return self._meta

    @property
    def searches(self) -> searches_pb2_grpc.SearchServiceStub:
        return self._searches


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
