import asyncio
import contextlib
from collections.abc import AsyncIterator, Awaitable, Callable, Sequence
from typing import TypeAlias

import grpc

from snowfall.project.junction.rocket.service.api.multi_modality import (
    repository,
    routes,
    search,
)
from snowfall.project.junction.rocket.service.api.v1alpha import multi_modal_pb2
from snowfall.project.junction.rocket.service.places.v1alpha import (
    models_pb2,
    places_pb2,
    places_pb2_grpc,
)
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import types as amqp_types


class SuggestionSearchNotFoundError(Exception):
    """Raised when no suggestion search is found."""


class PlaceNotFoundError(Exception):
    """Raised when a place is found."""


ProcessorImplementation: TypeAlias = Callable[
    [multi_modal_pb2.SuggestionSearchTask],
    Awaitable[None],
]


class SuggestionSearchProcessor:
    def __init__(
        self,
        suggestion_search_repository: repository.SuggestionSearchRepository,
        suggestion_repository: repository.SuggestionRepository,
        places: places_pb2_grpc.PlacesServiceStub,
        route_finder: routes.Routes,
        searcher: search.Searcher,
    ):
        self._search_repository = suggestion_search_repository
        self._suggestions = suggestion_repository
        self._places = places
        self._routes = route_finder
        self._searcher = searcher
        self._logger = stdout.get_logger()

    async def process(self, body: multi_modal_pb2.SuggestionSearchTask) -> None:
        async with self._get_search_to_process(body) as suggestion_search:
            try:
                await self._process(suggestion_search)
            except* search.ValidationError:
                self._logger.warning("Search criteria did not validate")
            except* search.ProviderTimeoutError:
                self._logger.warning("One of the underlying providers timed out")
            except* search.SearchError:
                self._logger.info("No results found, search failed")

    async def _process(
        self,
        suggestion_search: multi_modal_pb2.SuggestionSearch,
    ) -> None:
        possible_exceptions = await asyncio.gather(
            *[
                self._find_suggestions(suggestion_search, route)
                for route in await self._find_optimal_routes(suggestion_search)
            ],
            return_exceptions=True,
        )

        exceptions = list(filter(None, possible_exceptions))

        if exceptions:
            raise BaseExceptionGroup("One or more searches failed", exceptions)

    @contextlib.asynccontextmanager
    async def _get_search_to_process(
        self,
        body: multi_modal_pb2.SuggestionSearchTask,
    ) -> AsyncIterator[multi_modal_pb2.SuggestionSearch]:
        suggestion_search = await self._search_repository.find_by_id(
            body.suggestion_search_id,
        )

        if suggestion_search is None:
            raise SuggestionSearchNotFoundError("Suggestion search not found")

        await self._search_repository.mark_as_processing(suggestion_search.id)

        try:
            yield suggestion_search
        except Exception:
            await self._search_repository.mark_as_failed(suggestion_search.id)
            raise

        await self._search_repository.mark_as_completed(suggestion_search.id)

    async def _find_optimal_routes(
        self,
        suggestion_search: multi_modal_pb2.SuggestionSearch,
    ) -> list[routes.Route]:
        origin, destination = await self._get_origin_destination(suggestion_search)
        found_routes = await self._routes.find_routes(origin, destination)

        return self._select_optimal_routes(found_routes)

    def _select_optimal_routes(
        self,
        routes_to_optimize: Sequence[routes.Route],
    ) -> list[routes.Route]:
        return [
            routes_to_optimize[0],
        ]  # TODO(bolmis): Actually select the optimal routes.

    async def _get_origin_destination(
        self,
        suggestion_search: multi_modal_pb2.SuggestionSearch,
    ) -> tuple[models_pb2.Place, models_pb2.Place]:
        criteria = suggestion_search.criteria

        try:
            (origin_response, destination_response) = await asyncio.gather(
                self._places.GetPlace(
                    places_pb2.GetPlaceRequest(id=criteria.origin_id),
                ),
                self._places.GetPlace(
                    places_pb2.GetPlaceRequest(id=criteria.destination_id),
                ),
            )
        except grpc.aio.AioRpcError as place_err:
            raise PlaceNotFoundError() from place_err

        return origin_response.place, destination_response.place

    async def _find_suggestions(
        self,
        suggestion_search: multi_modal_pb2.SuggestionSearch,
        route: routes.Route,
    ) -> None:
        criteria = suggestion_search.criteria
        inbound = None

        if criteria.return_departure_after.year:
            inbound = search.TripRequest(
                route=route.to_inverse(),
                departure_after=protobuf.protobuf_to_datetime(
                    criteria.return_departure_after,
                ),
            )

        try:
            search_results = await self._searcher.find_results(
                search.SearchRequest(
                    outbound=search.TripRequest(
                        route=route,
                        departure_after=protobuf.protobuf_to_datetime(
                            criteria.departure_after,
                        ),
                    ),
                    inbound=inbound,
                    date_of_births=[
                        protobuf.protobuf_to_date(passenger.date_of_birth)
                        for passenger in criteria.passengers
                    ],
                    reseller_id=criteria.reseller_id,
                ),
            )
        except search.ModeNotSupportedForResellerError as err:
            self._logger.warning(str(err))
            return

        suggestion = search_results.optimize()

        await self._suggestions.create(
            suggestion_search_id=suggestion_search.id,
            suggestion=suggestion,
        )


class SuggestionSearchQueue(
    amqp_consumer.AbstractQueue[multi_modal_pb2.SuggestionSearchTask],
):
    def __init__(self, name_prefix: str, processor: ProcessorImplementation):
        self._name_prefix = name_prefix
        self._processor = processor
        self._logger = stdout.get_logger()

    @property
    def binds(self) -> list[tuple[amqp_types.Exchange, str]]:
        return [
            (amqp_types.Exchange(self._name_prefix), "tasks.suggestion_search"),
        ]

    @property
    def name(self) -> str:
        return "{0}_suggestion_searches".format(self._name_prefix)

    async def on_message(
        self,
        msg: amqp_types.Message[multi_modal_pb2.SuggestionSearchTask],
    ) -> None:
        with stdout.context_binding(suggestion_search_id=msg.body.suggestion_search_id):
            try:
                await self._processor(msg.body)
            except SuggestionSearchNotFoundError:
                self._logger.warning("Suggestion search not found")
                await msg.nack()
            except PlaceNotFoundError:
                self._logger.warning("Origin or destination not found")
                await msg.nack()
