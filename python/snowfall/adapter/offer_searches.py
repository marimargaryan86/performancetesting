from __future__ import annotations

import abc
import datetime
import uuid
from typing import Optional

import grpc

from snowfall.junction.offers.v1alpha import offers_pb2, offers_pb2_grpc
from snowfall.stdlib.format import protobuf


class NotFoundError(Exception):
    """Raised when an offer search resource is not found."""


class UnknownError(Exception):
    """Raised when an unhandled error occurs."""


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(
        self,
        request: offers_pb2.OfferSearch,
    ) -> offers_pb2.OfferSearch:
        """Create an offer search."""

    @abc.abstractmethod
    async def get(self, identifier: str) -> offers_pb2.OfferSearch:
        """Get an offer search."""

    @abc.abstractmethod
    async def find_offers(
        self,
        identifier: str,
        limit: int,
        cursor: Optional[str] = None,
    ) -> list[offers_pb2.OfferAggregate]:
        """Get offer results for an offer search."""


class DictClient(Client):
    def __init__(self) -> None:
        self._searches: dict[str, offers_pb2.OfferSearch] = {}

    async def create(
        self,
        request: offers_pb2.OfferSearch,
    ) -> offers_pb2.OfferSearch:
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            days=1,
        )
        offer_search = offers_pb2.OfferSearch(
            id=str(uuid.uuid4()),
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            trip=request.trip,
        )
        self._searches[offer_search.id] = offer_search

        return offer_search

    async def get(self, identifier: str) -> offers_pb2.OfferSearch:
        try:
            return self._searches[identifier]
        except KeyError:
            raise NotFoundError()

    async def find_offers(
        self,
        identifier: str,
        limit: int,
        cursor: Optional[str] = None,
    ) -> list[offers_pb2.OfferAggregate]:
        return []


class GrpcClient(Client):
    def __init__(
        self,
        offers: offers_pb2_grpc.OfferServiceStub,
        offer_searches: offers_pb2_grpc.OfferSearchServiceStub,
    ):
        self._offers = offers
        self._offer_searches = offer_searches

    async def create(
        self,
        request: offers_pb2.OfferSearch,
    ) -> offers_pb2.OfferSearch:
        try:
            response = await self._offer_searches.EnqueueOfferSearch(
                offers_pb2.EnqueueOfferSearchRequest(search=request),
            )
        except grpc.aio.AioRpcError as exc:
            raise UnknownError(exc.details()) from exc

        return response.search

    async def get(self, offer_search_id: str) -> offers_pb2.OfferSearch:
        try:
            response = await self._offer_searches.GetOfferSearch(
                offers_pb2.GetOfferSearchRequest(id=offer_search_id),
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Offer Search with ID '{id}' not found.".format(id=offer_search_id),
                ) from exc

            raise UnknownError(exc.details()) from exc

        return response.search

    async def find_offers(
        self,
        identifier: str,
        limit: int,
        cursor: Optional[str] = None,
    ) -> list[offers_pb2.OfferAggregate]:
        try:
            response = await self._offers.ListOffers(
                offers_pb2.ListOffersRequest(
                    page_size=limit,
                    page_token=cursor or "",
                    offer_search_id=identifier,
                ),
            )
        except grpc.aio.AioRpcError as exc:
            raise UnknownError(exc.details()) from exc

        return response.offers
