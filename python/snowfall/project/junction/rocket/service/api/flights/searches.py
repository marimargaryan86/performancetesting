import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeAlias

from snowfall.project.junction.rocket.service.api.flights import models, repositories
from snowfall.project.junction.rocket.service.api.flights.transforms import transforms
from snowfall.project.junction.rocket.service.api.v1alpha import search_pb2
from snowfall.project.junction.rocket.service.places.v1alpha import (
    places_pb2_grpc,
)
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.vendor.junction_one import auth as j1_auth
from snowfall.vendor.junction_one import client, errors

ProcessorImplementation: TypeAlias = Callable[
    [search_pb2.SearchTask],
    Awaitable[None],
]


class SearchProcessor:
    def __init__(
        self,
        results_repository: repositories.FlightSearchResultRepository,
        places: places_pb2_grpc.PlacesServiceStub,
        junction_one_client: client.JunctionOneClient,
        auth: j1_auth.TemporaryTokenAuth,
    ):
        self._results_repository = results_repository
        self._places = places
        self._junction_one_client = junction_one_client
        self._auth = auth
        self._flight_search_request_transformer = (
            transforms.FlightSearchRequestTransformer()
        )
        self._flight_search_result_transformer = (
            transforms.FlightSearchResultTransformer()
        )

    async def perform_search(self, task: search_pb2.SearchTask) -> None:
        search_request = models.FlightSearchRequest.model_validate_json(
            task.search_request_data,
        )
        relationships = search_request.data.relationships

        if relationships.selected_outbound_offer:
            outbound_flight_ref_id = await self._get_selected_outbound_offer_ref_ids(
                outbound_offer_id=relationships.selected_outbound_offer.data.id,
            )

            query = (
                await self._flight_search_request_transformer.transform_inbound_query(
                    search_request,
                    outbound_flight_ref_id,
                    self._places,
                )
            )
        else:
            query = (
                await self._flight_search_request_transformer.transform_outbound_query(
                    search_request,
                    self._places,
                )
            )

        with self._auth.temporary(task.reseller_id):
            j1_search_response = await self._junction_one_client.search_flights(query)

        transformed = self._flight_search_result_transformer.transform(
            j1_search_response,
            task.search_id,
        )

        await asyncio.gather(
            *(self._results_repository.insert(doc) for doc in transformed),
        )

    async def _get_selected_outbound_offer_ref_ids(
        self,
        outbound_offer_id: str,
    ) -> str:
        search_result = await self._results_repository.find_result_by_offer_id(
            outbound_offer_id,
        )
        selected_offer = next(
            offer for offer in search_result.offers if offer.id == outbound_offer_id
        )
        return selected_offer.ref_ids[0]


class FlightSearchQueue(
    amqp_consumer.AbstractQueue[search_pb2.SearchTask],
):
    def __init__(self, name_prefix: str, processor: ProcessorImplementation):
        self._name_prefix = name_prefix
        self._processor = processor
        self._logger = stdout.get_logger()

    @property
    def binds(self) -> list[tuple[amqp_types.Exchange, str]]:
        return [
            (amqp_types.Exchange(self._name_prefix), "tasks.flight_search"),
        ]

    @property
    def name(self) -> str:
        return "{0}_flight_searches".format(self._name_prefix)

    async def on_message(
        self,
        msg: amqp_types.Message[search_pb2.SearchTask],
    ) -> None:
        with stdout.context_binding(search_id=msg.body.search_id):
            try:
                await self._processor(msg.body)
            except errors.JunctionOneError:
                self._logger.exception("J1 search failed")
                await msg.nack()
