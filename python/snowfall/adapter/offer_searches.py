from __future__ import annotations

import abc
import datetime
import uuid

from snowfall.format import protobuf
from snowfall.junction.offers.v1alpha import offers_pb2


class NotFoundError(Exception):
    """Raised when an offer search resource is not found."""


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(
        self,
        request: offers_pb2.SearchTripOffersRequest,
    ) -> offers_pb2.OfferSearch:
        """Create an offer search."""

    @abc.abstractmethod
    async def get(self, identifier: str) -> offers_pb2.OfferSearch:
        """Get an offer search."""


class DictClient(Client):
    def __init__(self) -> None:
        self._searches: dict[str, offers_pb2.OfferSearch] = {}

    async def create(
        self,
        request: offers_pb2.SearchTripOffersRequest,
    ) -> offers_pb2.OfferSearch:
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            days=1,
        )
        offer_search = offers_pb2.OfferSearch(
            id=str(uuid.uuid4()),
            expires_at=await protobuf.datetime_to_protobuf(expires_at),
            trip=request.search,
        )
        self._searches[offer_search.id] = offer_search

        return offer_search

    async def get(self, identifier: str) -> offers_pb2.OfferSearch:
        try:
            return self._searches[identifier]
        except KeyError:
            raise NotFoundError()
