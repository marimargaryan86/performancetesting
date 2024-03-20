from __future__ import annotations

import abc
import datetime
from collections.abc import Sequence

from snowfall.project.junction.rocket.adapter import errors
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import amqp_pb2


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(
        self,
        request: models_pb2.Search,
    ) -> models_pb2.Search:
        """Create a new Search."""

    @abc.abstractmethod
    async def get(
        self,
        identifier: str,
    ) -> models_pb2.Search:
        """Retrieve an existing Search by ID."""


class DictClient(Client):
    def __init__(self, searches: Sequence[models_pb2.Search]) -> None:
        self._searches = {search.id: search for search in searches}

    async def create(self, request: models_pb2.Search) -> models_pb2.Search:
        expires_at = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)
        search = models_pb2.Search(
            id=string.uuid(),
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            status=amqp_pb2.Trackable.Status.STATUS_PROCESSING,
            reseller_id=request.reseller_id,
            mock=request.mock,
        )
        self._searches[search.id] = search

        return search

    async def get(self, identifier: str) -> models_pb2.Search:
        try:
            return self._searches[identifier]
        except KeyError as err:
            raise errors.NotFoundError() from err


class GrpcClient(Client):
    def __init__(
        self,
        searches: grpc_pb2_grpc.SearchServiceStub,
        timeout: int = 10,
    ):
        self._searches = searches
        self._timeout = timeout

    async def create(
        self,
        request: models_pb2.Search,
    ) -> models_pb2.Search:
        response = await errors.handle_grpc_errors(
            self._searches.EnqueueSearch(
                grpc_pb2.EnqueueSearchRequest(
                    search=request,
                ),
                timeout=self._timeout,
            ),
        )

        return response.search

    async def get(self, identifier: str) -> models_pb2.Search:
        response = await errors.handle_grpc_errors(
            self._searches.GetSearch(
                grpc_pb2.GetSearchRequest(id=identifier),
                timeout=self._timeout,
            ),
        )

        return response.search
