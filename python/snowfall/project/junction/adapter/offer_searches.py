from __future__ import annotations

import abc
import datetime
from typing import Sequence

from snowfall.project.junction.adapter import errors
from snowfall.project.junction.service.offers.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(
        self,
        request: models_pb2.OfferSearch,
    ) -> models_pb2.OfferSearch:
        """Create an offer search."""

    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.OfferSearch:
        """Get an offer search."""

    @abc.abstractmethod
    async def find_by_ids(self, ids: Sequence[str]) -> Sequence[models_pb2.OfferSearch]:
        """Get multiple offer searches."""


class DictClient(Client):
    def __init__(self, offer_searches: Sequence[models_pb2.OfferSearch]) -> None:
        self._searches: dict[str, models_pb2.OfferSearch] = {
            offer_search.id: offer_search for offer_search in offer_searches
        }

    async def create(
        self,
        request: models_pb2.OfferSearch,
    ) -> models_pb2.OfferSearch:
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            days=1,
        )
        offer_search = models_pb2.OfferSearch(
            id=string.uuid(),
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            trip=request.trip,
        )
        self._searches[offer_search.id] = offer_search

        return offer_search

    async def get(self, identifier: str) -> models_pb2.OfferSearch:
        try:
            return self._searches[identifier]
        except KeyError as err:
            raise errors.NotFoundError() from err

    async def find_by_ids(self, ids: Sequence[str]) -> Sequence[models_pb2.OfferSearch]:
        return [
            self._searches[identifier]
            for identifier in ids
            if identifier in self._searches
        ]


class GrpcClient(Client):
    def __init__(
        self,
        offer_searches: grpc_pb2_grpc.OfferSearchServiceStub,
        timeout: int = 10,
    ):
        self._offer_searches = offer_searches
        self._timeout = timeout

    async def create(
        self,
        request: models_pb2.OfferSearch,
    ) -> models_pb2.OfferSearch:
        response = await errors.handle_grpc_errors(
            self._offer_searches.EnqueueOfferSearch(
                grpc_pb2.EnqueueOfferSearchRequest(
                    search=request,
                ),
                timeout=self._timeout,
            ),
        )

        return response.search

    async def get(self, offer_search_id: str) -> models_pb2.OfferSearch:
        response = await errors.handle_grpc_errors(
            self._offer_searches.GetOfferSearch(
                grpc_pb2.GetOfferSearchRequest(id=offer_search_id),
                timeout=self._timeout,
            ),
        )

        return response.search

    async def find_by_ids(self, ids: Sequence[str]) -> Sequence[models_pb2.OfferSearch]:
        response = await errors.handle_grpc_errors(
            self._offer_searches.ListOfferSearches(
                grpc_pb2.ListOfferSearchesRequest(ids=ids),
                timeout=self._timeout,
            ),
        )

        return response.offer_searches
