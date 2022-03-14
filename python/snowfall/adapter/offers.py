from __future__ import annotations

import abc
import dataclasses
from typing import Optional, Sequence

import grpc

from snowfall.junction.offers.v1alpha import offers_pb2, offers_pb2_grpc


class NotFoundError(Exception):
    """Raised when a offer is not found."""


class UnknownError(Exception):
    """Raised when an unhandled error occurs."""


@dataclasses.dataclass(frozen=True)
class OffersPage(object):
    offers: Sequence[offers_pb2.OfferAggregate]
    next_page_token: Optional[str] = None

    @classmethod
    def from_proto(cls, grpc_offers: offers_pb2.ListOffersResponse) -> OffersPage:
        return cls(
            offers=grpc_offers.offers,
            next_page_token=grpc_offers.next_page_token,
        )


class Client(abc.ABC):
    @abc.abstractmethod
    async def get(self, identifier: str) -> offers_pb2.OfferAggregate:
        """Fetch a offer resource."""


class DictClient(Client):
    def __init__(self, offers: Sequence[offers_pb2.OfferAggregate]) -> None:
        self._offers = {offer.id: offer for offer in offers}

    async def get(self, offer_id: str) -> offers_pb2.OfferAggregate:
        if offer_id not in self._offers:
            raise NotFoundError()

        return offers_pb2.OfferAggregate(id=offer_id)


class GrpcClient(Client):
    def __init__(self, offers: offers_pb2_grpc.OfferServiceStub):
        self._offers = offers

    async def get(self, offer_id: str) -> offers_pb2.OfferAggregate:
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
