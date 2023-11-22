import contextlib
import datetime
import itertools
from collections.abc import AsyncGenerator, Sequence
from typing import TypeGuard

from snowfall.project.junction.go.service.gateway import providers, stops
from snowfall.project.junction.go.service.gateway.v1 import trips_pb2
from snowfall.project.junction.provider.v2alpha import meta_pb2 as provider_meta_pb2
from snowfall.project.junction.provider.v2alpha import trips_pb2 as provider_trips_pb2
from snowfall.project.junction.v1 import passenger_type_pb2
from snowfall.stdlib.format import protobuf

_GeneratorReturn = AsyncGenerator[
    tuple[providers.Provider, provider_trips_pb2.SearchTripsRequest],
    None,
]


class BuildError(Exception):
    """Raise when a request can't be built."""


def _build_multi_city(
    provider: providers.Provider,
    details: trips_pb2.MultiCity,
    passengers: Sequence[trips_pb2.Passenger],
    resolved_stops: stops.ResolvedMap,
) -> provider_trips_pb2.SearchTripsRequest:
    criteria = [
        _to_provider_criterion(
            provider,
            resolved_stops,
            criterion,
        )
        for criterion in details.criteria
    ]

    if not _criteria_is_valid(criteria):
        raise BuildError

    provider_passengers = _to_passengers(provider, passengers)

    if not provider_passengers:
        raise BuildError

    return provider_trips_pb2.SearchTripsRequest(
        multi_city=provider_trips_pb2.SearchTripsRequest.MultiCity(
            criteria=criteria,
        ),
        passengers=provider_passengers,
    )


def _build_one_way(
    provider: providers.Provider,
    details: trips_pb2.OneWay,
    passengers: Sequence[trips_pb2.Passenger],
    resolved_stops: stops.ResolvedMap,
) -> provider_trips_pb2.SearchTripsRequest:
    criterion = _to_provider_criterion(provider, resolved_stops, details.criterion)

    if not criterion:
        raise BuildError

    provider_passengers = _to_passengers(provider, passengers)

    if not provider_passengers:
        raise BuildError

    return provider_trips_pb2.SearchTripsRequest(
        one_way=provider_trips_pb2.SearchTripsRequest.OneWay(
            criterion=criterion,
        ),
        passengers=provider_passengers,
    )


def _build_round_trip(
    provider: providers.Provider,
    details: trips_pb2.RoundTrip,
    passengers: Sequence[trips_pb2.Passenger],
    resolved_stops: stops.ResolvedMap,
) -> provider_trips_pb2.SearchTripsRequest:
    criterion = _to_provider_criterion(
        provider,
        resolved_stops,
        details.criterion,
    )

    if not criterion:
        raise BuildError

    provider_passengers = _to_passengers(provider, passengers)

    if not provider_passengers:
        raise BuildError

    return provider_trips_pb2.SearchTripsRequest(
        round_trip=provider_trips_pb2.SearchTripsRequest.RoundTrip(
            criterion=criterion,
            return_date=details.return_date,
        ),
        passengers=provider_passengers,
    )


class Generator(object):
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
    ) -> _GeneratorReturn:
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
    ) -> _GeneratorReturn:
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
            if provider.trip_search_capabilities.supports_multi_city:
                with contextlib.suppress(BuildError):
                    yield (
                        provider,
                        _build_multi_city(
                            provider,
                            task.multi_city,
                            task.passengers,
                            resolved_stops,
                        ),
                    )
            else:
                requests = _multi_city_fallback(
                    provider,
                    task.multi_city,
                    task.passengers,
                    resolved_stops,
                )

                for request in requests:
                    yield provider, request

    async def _one_way(
        self,
        task: trips_pb2.TripSearchTask,
    ) -> _GeneratorReturn:
        resolved_stops = await self._stop_resolver(
            frozenset(
                (
                    task.one_way.criterion.origin,
                    task.one_way.criterion.destination,
                ),
            ),
        )

        for provider in await self._eligible_providers():
            with contextlib.suppress(BuildError):
                yield (
                    provider,
                    _build_one_way(
                        provider,
                        task.one_way,
                        task.passengers,
                        resolved_stops,
                    ),
                )

    async def _round_trip(
        self,
        task: trips_pb2.TripSearchTask,
    ) -> _GeneratorReturn:
        resolved_stops = await self._stop_resolver(
            frozenset(
                (
                    task.round_trip.criterion.origin,
                    task.round_trip.criterion.destination,
                ),
            ),
        )

        for provider in await self._eligible_providers():
            if provider.trip_search_capabilities.supports_round_trip:
                with contextlib.suppress(BuildError):
                    yield (
                        provider,
                        _build_round_trip(
                            provider,
                            task.round_trip,
                            task.passengers,
                            resolved_stops,
                        ),
                    )
            else:
                requests = _round_trip_fallback(
                    provider,
                    task.round_trip,
                    task.passengers,
                    resolved_stops,
                )

                for request in requests:
                    yield provider, request

    async def _eligible_providers(self) -> list[providers.Provider]:
        return [
            provider
            async for provider in self._providers.all_healthy()
            if provider.trip_search_capabilities.is_supported
        ]


def _multi_city_fallback(
    provider: providers.Provider,
    details: trips_pb2.MultiCity,
    passengers: Sequence[trips_pb2.Passenger],
    resolved_stops: stops.ResolvedMap,
) -> Sequence[provider_trips_pb2.SearchTripsRequest]:
    one_ways = [trips_pb2.OneWay(criterion=criterion) for criterion in details.criteria]

    try:
        return [
            _build_one_way(provider, details, passengers, resolved_stops)
            for details in one_ways
        ]
    except BuildError:
        return []


def _round_trip_fallback(
    provider: providers.Provider,
    details: trips_pb2.RoundTrip,
    passengers: Sequence[trips_pb2.Passenger],
    resolved_stops: stops.ResolvedMap,
) -> Sequence[provider_trips_pb2.SearchTripsRequest]:
    one_ways = [
        trips_pb2.OneWay(
            criterion=details.criterion,
        ),
        trips_pb2.OneWay(
            criterion=trips_pb2.Criterion(
                origin=details.criterion.destination,
                destination=details.criterion.origin,
                departure_date=details.return_date,
                segment_types=details.criterion.segment_types,
                max_connections=details.criterion.max_connections,
            ),
        ),
    ]

    try:
        return [
            _build_one_way(provider, details, passengers, resolved_stops)
            for details in one_ways
        ]
    except BuildError:
        return []


def _to_passengers(
    provider: providers.Provider,
    passengers: Sequence[trips_pb2.Passenger],
) -> list[provider_trips_pb2.SearchTripsRequest.Passenger]:
    match provider.trip_search_capabilities.passenger_age_identification_method:
        case provider_meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_PROVIDER_TYPE:
            # TODO(jyggen): implement
            return []
        case provider_meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH:
            return [
                provider_trips_pb2.SearchTripsRequest.Passenger(
                    date_of_birth=protobuf.date_to_protobuf(
                        _passenger_type_to_date_of_birth(passenger.type),
                    ),
                )
                for passenger in passengers
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
    if not _provider_supports_any_segment_type(provider, criterion):
        return None

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
            # TODO(jyggen): implement
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


def _provider_supports_any_segment_type(
    provider: providers.Provider,
    criterion: trips_pb2.Criterion,
) -> bool:
    if not criterion.segment_types:
        return True

    return any(
        True
        for type_ in criterion.segment_types
        if type_ in provider.trip_search_capabilities.supported_segment_types
    )
