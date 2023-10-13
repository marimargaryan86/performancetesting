import asyncio
import datetime
import itertools
import time
from collections.abc import AsyncGenerator, Sequence
from typing import TypeGuard

import prometheus_client
from grpc import aio

from snowfall.project.junction.go.service.gateway import providers, stops, tasks
from snowfall.project.junction.go.service.gateway.v1 import trips_pb2, trips_pb2_grpc
from snowfall.project.junction.provider.v2alpha import meta_pb2 as provider_meta_pb2
from snowfall.project.junction.provider.v2alpha import trips_pb2 as provider_trips_pb2
from snowfall.project.junction.v1 import passenger_type_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.instrumentation import prometheus
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer, protocol, types
from snowfall.stdlib.transport.grpc import service


class Service(service.Service, trips_pb2_grpc.TripServiceServicer):
    def __init__(
        self,
        producer: protocol.Producer,
        runner: tasks.Runner[trips_pb2.TripSearchResult],
    ):
        self._producer = producer
        self._runner = runner

    def get_name(self) -> str:
        return trips_pb2.DESCRIPTOR.services_by_name["TripService"].full_name

    def register(self, server: aio.Server) -> None:
        trips_pb2_grpc.add_TripServiceServicer_to_server(self, server)

    async def EnqueueTripSearch(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.EnqueueTripSearchRequest,
        context: aio.ServicerContext,
    ) -> trips_pb2.EnqueueTripSearchResponse:
        trip_search_id = string.uuid()

        await asyncio.gather(
            self._producer.publish(
                trips_pb2.TripSearchTask(
                    id=trip_search_id,
                    one_way=request.one_way,
                    round_trip=request.round_trip,
                    multi_city=request.multi_city,
                    passengers=request.passengers,
                ),
                "tasks.trip_search",
            ),
            self._runner.mark_as_in_progress(trip_search_id),
        )

        return trips_pb2.EnqueueTripSearchResponse(id=trip_search_id)

    async def DrainTripSearchResults(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.DrainTripSearchResultsRequest,
        context: aio.ServicerContext,
    ) -> trips_pb2.DrainTripSearchResultsResponse:
        return trips_pb2.DrainTripSearchResultsResponse(
            is_in_progress=await self._runner.is_in_progress(request.id),
            results=await self._runner.drain_results(request.id),
        )


_RequestGeneratorReturn = AsyncGenerator[
    tuple[providers.Provider, provider_trips_pb2.SearchTripsRequest],
    None,
]


class RequestGenerator(object):
    def __init__(
        self,
        providers_list: providers.Collection,
        stop_resolver: stops.ResolverFunc,
    ) -> None:
        self._providers = providers_list
        self._stop_resolver = stop_resolver

    async def generate(
        self,
        task: trips_pb2.TripSearchTask,
    ) -> _RequestGeneratorReturn:
        match task.WhichOneof("search_mode"):
            case "one_way":
                provider_request_tuple_generator = self._one_way(task)
            case "round_trip":
                provider_request_tuple_generator = self._round_trip(task)
            case "multi_city":
                provider_request_tuple_generator = self._multi_city(task)
            case _:
                return

        async for provider_request_tuple in provider_request_tuple_generator:
            yield provider_request_tuple

    async def _multi_city(
        self,
        task: trips_pb2.TripSearchTask,
    ) -> _RequestGeneratorReturn:
        resolved_stops = await self._stop_resolver(
            frozenset(
                itertools.chain(
                    *[
                        [
                            criterion.origin,
                            criterion.destination,
                        ]
                        for criterion in task.multi_city.criteria
                    ],
                ),
            ),
        )

        for provider in await self._eligible_providers():
            # TODO: use supports_multi_city and supported_segment_types flags

            criteria = [
                _to_provider_criterion(
                    provider,
                    resolved_stops,
                    criterion,
                )
                for criterion in task.multi_city.criteria
            ]

            if not _criteria_is_valid(criteria):
                continue

            passengers = _to_passengers(provider, task)

            if not passengers:
                continue

            yield provider, provider_trips_pb2.SearchTripsRequest(
                multi_city=provider_trips_pb2.SearchTripsRequest.MultiCity(
                    criteria=criteria,
                ),
                passengers=passengers,
            )

    async def _one_way(
        self,
        task: trips_pb2.TripSearchTask,
    ) -> _RequestGeneratorReturn:
        resolved_stops = await self._stop_resolver(
            frozenset(
                (
                    task.one_way.criterion.origin,
                    task.one_way.criterion.destination,
                ),
            ),
        )

        for provider in await self._eligible_providers():
            # TODO: use supported_segment_types flags

            criterion = _to_provider_criterion(
                provider,
                resolved_stops,
                task.one_way.criterion,
            )

            if not criterion:
                continue

            passengers = _to_passengers(provider, task)

            if not passengers:
                continue

            yield provider, provider_trips_pb2.SearchTripsRequest(
                one_way=provider_trips_pb2.SearchTripsRequest.OneWay(
                    criterion=criterion,
                ),
                passengers=passengers,
            )

    async def _round_trip(
        self,
        task: trips_pb2.TripSearchTask,
    ) -> _RequestGeneratorReturn:
        resolved_stops = await self._stop_resolver(
            frozenset(
                (
                    task.round_trip.criterion.origin,
                    task.round_trip.criterion.destination,
                ),
            ),
        )

        for provider in await self._eligible_providers():
            # TODO: use supports_round_trip and supported_segment_types flags

            criterion = _to_provider_criterion(
                provider,
                resolved_stops,
                task.round_trip.criterion,
            )

            if not criterion:
                continue

            passengers = _to_passengers(provider, task)

            if not passengers:
                continue

            yield provider, provider_trips_pb2.SearchTripsRequest(
                round_trip=provider_trips_pb2.SearchTripsRequest.RoundTrip(
                    criterion=criterion,
                    return_date=task.round_trip.return_date,
                ),
                passengers=passengers,
            )

    async def _eligible_providers(self) -> list[providers.Provider]:
        return [
            provider
            async for provider in self._providers.all_healthy()
            if provider.trip_search_capabilities.is_supported
        ]


def _to_passengers(
    provider: providers.Provider,
    task: trips_pb2.TripSearchTask,
) -> list[provider_trips_pb2.SearchTripsRequest.Passenger]:
    match provider.trip_search_capabilities.passenger_age_identification_method:
        case provider_meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_PROVIDER_TYPE:
            # TODO: implement
            return []
        case provider_meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH:
            return [
                provider_trips_pb2.SearchTripsRequest.Passenger(
                    date_of_birth=protobuf.date_to_protobuf(
                        _passenger_type_to_date_of_birth(passenger.type),
                    ),
                )
                for passenger in task.passengers
                if passenger.type is not passenger_type_pb2.PASSENGER_TYPE_UNSPECIFIED
            ]

    return []


_ADULT_AGE = 30
_CHILD_AGE = 8
_INFANT_AGE = 1


def _criteria_is_valid(
    criteria: Sequence[provider_trips_pb2.SearchTripsRequest.Criterion | None],
) -> TypeGuard[Sequence[provider_trips_pb2.SearchTripsRequest.Criterion]]:
    return bool(criteria and all(criteria))


def _passenger_type_to_date_of_birth(
    passenger_type: passenger_type_pb2.PassengerType.ValueType,
) -> datetime.date:
    today = datetime.datetime.now(tz=datetime.UTC).date()
    base_date = today.replace(month=1, day=1)

    match passenger_type:
        case passenger_type_pb2.PASSENGER_TYPE_ADULT:
            return base_date.replace(year=base_date.year - _ADULT_AGE)
        case passenger_type_pb2.PASSENGER_TYPE_CHILD:
            return base_date.replace(year=base_date.year - _CHILD_AGE)
        case passenger_type_pb2.PASSENGER_TYPE_INFANT:
            return base_date.replace(year=base_date.year - _INFANT_AGE)
        case _:
            return base_date


def _to_provider_criterion(
    provider: providers.Provider,
    stops_mapping: stops.ResolvedMap,
    criterion: trips_pb2.Criterion,
) -> provider_trips_pb2.SearchTripsRequest.Criterion | None:
    try:
        origin = stops_mapping[criterion.origin]
    except KeyError:
        return None

    try:
        destination = stops_mapping[criterion.destination]
    except KeyError:
        return None

    provider_criterion = provider_trips_pb2.SearchTripsRequest.Criterion(
        departure_date=criterion.departure_date,
    )

    match provider.trip_search_capabilities.stop_identification_method:
        case provider_meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_PROVIDER_IDS:
            # TODO: implement
            return None
        case provider_meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_COORDINATES:
            provider_criterion.origin_coordinates.CopyFrom(
                origin.location.coordinates,
            )
            provider_criterion.destination_coordinates.CopyFrom(
                destination.location.coordinates,
            )
        case provider_meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_IATA_CODES:
            provider_criterion.origin_identifier = origin.place_attributes.iata
            provider_criterion.destination_identifier = (
                destination.place_attributes.iata
            )

    if not _provider_criterion_is_valid(provider_criterion):
        return None

    return provider_criterion


def _provider_criterion_is_valid(
    criterion: provider_trips_pb2.SearchTripsRequest.Criterion,
) -> bool:
    return any(
        [
            criterion.origin_identifier,
            criterion.origin_coordinates.latitude,
            criterion.origin_coordinates.longitude,
        ],
    ) and any(
        [
            criterion.destination_identifier,
            criterion.destination_coordinates.latitude,
            criterion.destination_coordinates.longitude,
        ],
    )


class Queue(consumer.AbstractQueue[trips_pb2.TripSearchTask]):
    def __init__(
        self,
        name_prefix: str,
        request_generator: RequestGenerator,
        runner: tasks.Runner[trips_pb2.TripSearchResult],
        timeout: datetime.timedelta,
    ):
        self._request_generator = request_generator
        self._name_prefix = name_prefix
        self._runner = runner
        self._searcher = Searcher(timeout)

    @property
    def binds(self) -> Sequence[tuple[types.Exchange, str]]:
        return [
            (types.Exchange(self._name_prefix), "trips.search.*"),
        ]

    @property
    def name(self) -> str:
        return "{0}_trip_searches".format(self._name_prefix)

    async def on_message(self, msg: types.Message[trips_pb2.TripSearchTask]) -> None:
        await self._runner.run(msg.body.id, self._on_message(msg.body))

    async def _on_message(
        self,
        body: trips_pb2.TripSearchTask,
    ) -> AsyncGenerator[trips_pb2.TripSearchResult, None]:
        search_tasks = [
            self._searcher.search(provider, request)
            async for provider, request in self._request_generator.generate(body)
        ]

        for task in asyncio.as_completed(search_tasks):
            for search_result in (await task).results:
                yield trips_pb2.TripSearchResult(
                    id=string.uuid(),
                    result=search_result,
                )


class Searcher(object):
    _failed = prometheus_client.Counter(
        "gateway_failed_trip_searches_total",
        "Total number of failed trip searches",
        ["provider_id"],
    )

    _histogram = prometheus_client.Histogram(
        "gateway_trip_search_duration_seconds",
        "Duration of performed trip searches in seconds",
        ["provider_id", "status"],
        buckets=prometheus.BUCKETS,
    )

    _total = prometheus_client.Counter(
        "gateway_trip_searches_total",
        "Total number of performed trip searches",
        ["provider_id", "status"],
    )

    def __init__(self, timeout: datetime.timedelta):
        self._logger = stdout.get_logger()
        self._timeout = timeout

    async def search(
        self,
        provider: providers.Provider,
        request: provider_trips_pb2.SearchTripsRequest,
    ) -> provider_trips_pb2.SearchTripsResponse:
        start = time.perf_counter()
        status = "ok"

        try:
            response = await provider.connection.trips.SearchTrips(
                request=request,
                timeout=self._timeout.total_seconds(),
            )
        except aio.AioRpcError:
            self._failed.labels(provider_id=provider.identifier).inc()
            response = provider_trips_pb2.SearchTripsResponse()
            status = "nok"
        finally:
            exec_time = time.perf_counter() - start

        self._histogram.labels(provider_id=provider.identifier, status=status).observe(
            exec_time,
        )
        self._total.labels(provider_id=provider.identifier, status=status).inc()
        self._logger.info(
            "trip search performed",
            provider_id=provider.identifier,
            failed=status == "nok",
            results=len(response.results),
            execution_time=exec_time,
        )

        return response
