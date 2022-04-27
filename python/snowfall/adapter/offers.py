from __future__ import annotations

import abc
import dataclasses
from typing import Optional, Sequence

import grpc

from snowfall.junction.offers.v1alpha import offers_pb2, offers_pb2_grpc


class NotFoundError(Exception):
    """Raised when an offer is not found."""


class UnknownError(Exception):
    """Raised when an unhandled error occurs."""


@dataclasses.dataclass(frozen=True)
class OffersPage(object):
    offers: Sequence[offers_pb2.Offer]
    next_page_token: Optional[str] = None

    @classmethod
    def from_proto(cls, grpc_offers: offers_pb2.ListOffersResponse) -> OffersPage:
        return cls(
            offers=grpc_offers.offers,
            next_page_token=grpc_offers.next_page_token,
        )


class Client(abc.ABC):
    @abc.abstractmethod
    async def get(self, identifier: str) -> offers_pb2.Offer:
        """Fetch an offer resource."""

    @abc.abstractmethod
    async def find_offers_by_offer_search(
        self,
        identifier: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> OffersPage:
        """Get offer results for an offer search."""

    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> OffersPage:
        """Return offers by offer ids."""


class DictClient(Client):
    def __init__(self, offers: Sequence[offers_pb2.Offer]) -> None:
        self._offers = {offer.id: offer for offer in offers}

    async def get(self, offer_id: str) -> offers_pb2.Offer:
        if offer_id not in self._offers:
            raise NotFoundError()

        return self._offers[offer_id]

    async def find_offers_by_offer_search(
        self,
        identifier: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> OffersPage:
        return OffersPage(
            offers=[
                offer
                for offer in self._offers.values()
                if offer.results and offer.results[0].offer_search_id == identifier
            ],
        )

    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> OffersPage:
        return OffersPage(
            [
                self._offers[identifier]
                for identifier in identifiers
                if identifier in self._offers
            ],
        )


class GrpcClient(Client):
    def __init__(self, offers: offers_pb2_grpc.OfferServiceStub):
        self._offers = offers

    async def get(self, offer_id: str) -> offers_pb2.Offer:
        try:
            response = await self._offers.GetOffer(
                offers_pb2.GetOfferRequest(id=offer_id),
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Offer with ID '{id}' not found.".format(id=offer_id),
                ) from exc

            raise UnknownError() from exc

        return response.offer

    async def find_offers_by_offer_search(
        self,
        identifier: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> OffersPage:
        request = offers_pb2.ListOffersRequest(
            page_token=cursor or "",
            offer_search_id=identifier,
        )
        if limit is not None:
            request.page_size = limit

        try:
            response = await self._offers.ListOffers(request)
        except grpc.aio.AioRpcError as exc:
            raise UnknownError(exc.details()) from exc

        return OffersPage(
            offers=response.offers,
            next_page_token=response.next_page_token,
        )

    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> OffersPage:
        request = offers_pb2.ListOffersRequest(
            page_token=cursor or "",
            offer_ids=offers_pb2.ListOfOfferIds(
                ids=list(identifiers),
            ),
        )
        if limit is not None:
            request.page_size = limit

        try:
            response = await self._offers.ListOffers(request)
        except grpc.aio.AioRpcError as exc:
            raise UnknownError() from exc

        return OffersPage(
            offers=list(response.offers),
            next_page_token=response.next_page_token,
        )
