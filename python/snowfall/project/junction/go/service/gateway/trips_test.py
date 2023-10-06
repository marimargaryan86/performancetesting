from collections.abc import AsyncIterable, Callable

import pytest
from google.protobuf import json_format
from grpc import aio
from pytest_mock import plugin

from snowfall.project.junction.go.service.gateway import providers, stops, trips
from snowfall.project.junction.go.service.gateway.v1 import trips_pb2
from snowfall.project.junction.go.service.places.v1 import models_pb2
from snowfall.project.junction.provider.v2alpha import meta_pb2
from snowfall.project.junction.provider.v2alpha import trips_pb2 as provider_trips_pb2
from snowfall.stdlib.v1 import date_pb2, latlng_pb2

_ORIGIN_IDENTIFIER = "foobar"
_ORIGIN_IATA = "FOO"
_DESTINATION_IDENTIFIER = "bazqux"
_DESTINATION_IATA = "BAZ"
_NO_IATA_IDENTIFIER = "no_iata"
_DEPARTURE_DATE = date_pb2.Date(year=2023, month=10, day=25)
_RETURN_DATE = date_pb2.Date(year=2023, month=11, day=25)
_PASSENGER_DOB = date_pb2.Date(year=1990, month=10, day=25)
_ORIGIN_COORDINATES = latlng_pb2.LatLng(
    latitude=1,
    longitude=1,
)
_DESTINATION_COORDINATES = latlng_pb2.LatLng(
    latitude=-1,
    longitude=-1,
)
_TASK_PASSENGER = trips_pb2.Passenger(
    date_of_birth=_PASSENGER_DOB,
)
_REQUEST_PASSENGER = provider_trips_pb2.SearchTripsRequest.Passenger(
    date_of_birth=_PASSENGER_DOB,
)
_ONE_WAY_TASK = trips_pb2.TripSearchTask(
    one_way=trips_pb2.OneWay(
        criterion=trips_pb2.Criterion(
            origin=_ORIGIN_IDENTIFIER,
            destination=_DESTINATION_IDENTIFIER,
            departure_date=_DEPARTURE_DATE,
        ),
    ),
    passengers=[_TASK_PASSENGER],
)
_MULTI_CITY_TASK = trips_pb2.TripSearchTask(
    multi_city=trips_pb2.MultiCity(
        criteria=[
            trips_pb2.Criterion(
                origin=_ORIGIN_IDENTIFIER,
                destination=_DESTINATION_IDENTIFIER,
                departure_date=_DEPARTURE_DATE,
            ),
            trips_pb2.Criterion(
                origin=_DESTINATION_IDENTIFIER,
                destination=_ORIGIN_IDENTIFIER,
                departure_date=_RETURN_DATE,
            ),
        ],
    ),
    passengers=[_TASK_PASSENGER],
)
_ROUND_TRIP_TASK = trips_pb2.TripSearchTask(
    round_trip=trips_pb2.RoundTrip(
        criterion=trips_pb2.Criterion(
            origin=_ORIGIN_IDENTIFIER,
            destination=_DESTINATION_IDENTIFIER,
            departure_date=_DEPARTURE_DATE,
        ),
        return_date=_RETURN_DATE,
    ),
    passengers=[_TASK_PASSENGER],
)


async def _stop_resolver(stops_ids: frozenset[str]) -> stops.ResolvedMap:
    return {
        identifier: model
        for identifier, model in {
            _ORIGIN_IDENTIFIER: models_pb2.Place(
                location=models_pb2.Location(
                    coordinates=_ORIGIN_COORDINATES,
                ),
                place_attributes=models_pb2.PlaceAttributes(
                    iata=_ORIGIN_IATA,
                ),
            ),
            _DESTINATION_IDENTIFIER: models_pb2.Place(
                location=models_pb2.Location(
                    coordinates=_DESTINATION_COORDINATES,
                ),
                place_attributes=models_pb2.PlaceAttributes(
                    iata=_DESTINATION_IATA,
                ),
            ),
            _NO_IATA_IDENTIFIER: models_pb2.Place(
                location=models_pb2.Location(
                    coordinates=_DESTINATION_COORDINATES,
                ),
                place_attributes=models_pb2.PlaceAttributes(),
            ),
        }.items()
        if identifier in stops_ids
    }


def _providers_factory(
    capabilities: meta_pb2.TripSearchCapabilities,
) -> Callable[[], AsyncIterable[providers.Provider]]:
    async def wrapper() -> AsyncIterable[providers.Provider]:
        yield providers.Provider(
            connection=providers.Connection(aio.insecure_channel("foobar")),
            name="",
            identifier="",
            trip_search_capabilities=capabilities,
        )

    return wrapper


class TestRequestGenerator(object):
    @pytest.mark.parametrize(
        ("task", "capabilities", "expected"),
        [
            pytest.param(
                _ONE_WAY_TASK,
                meta_pb2.TripSearchCapabilities(
                    is_supported=True,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_COORDINATES,
                ),
                provider_trips_pb2.SearchTripsRequest(
                    one_way=provider_trips_pb2.SearchTripsRequest.OneWay(
                        criterion=provider_trips_pb2.SearchTripsRequest.Criterion(
                            origin_coordinates=_ORIGIN_COORDINATES,
                            destination_coordinates=_DESTINATION_COORDINATES,
                            departure_date=_DEPARTURE_DATE,
                        ),
                    ),
                    passengers=[_REQUEST_PASSENGER],
                ),
                id="one way with coordinates identification method",
            ),
            pytest.param(
                _ONE_WAY_TASK,
                meta_pb2.TripSearchCapabilities(
                    is_supported=True,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_IATA_CODES,
                ),
                provider_trips_pb2.SearchTripsRequest(
                    one_way=provider_trips_pb2.SearchTripsRequest.OneWay(
                        criterion=provider_trips_pb2.SearchTripsRequest.Criterion(
                            origin_identifier=_ORIGIN_IATA,
                            destination_identifier=_DESTINATION_IATA,
                            departure_date=_DEPARTURE_DATE,
                        ),
                    ),
                    passengers=[_REQUEST_PASSENGER],
                ),
                id="one way with IATA codes identification method",
            ),
            pytest.param(
                _MULTI_CITY_TASK,
                meta_pb2.TripSearchCapabilities(
                    is_supported=True,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_COORDINATES,
                ),
                provider_trips_pb2.SearchTripsRequest(
                    multi_city=provider_trips_pb2.SearchTripsRequest.MultiCity(
                        criteria=[
                            provider_trips_pb2.SearchTripsRequest.Criterion(
                                origin_coordinates=_ORIGIN_COORDINATES,
                                destination_coordinates=_DESTINATION_COORDINATES,
                                departure_date=_DEPARTURE_DATE,
                            ),
                            provider_trips_pb2.SearchTripsRequest.Criterion(
                                origin_coordinates=_DESTINATION_COORDINATES,
                                destination_coordinates=_ORIGIN_COORDINATES,
                                departure_date=_RETURN_DATE,
                            ),
                        ],
                    ),
                    passengers=[_REQUEST_PASSENGER],
                ),
                id="multi city with coordinates identification method",
            ),
            pytest.param(
                _MULTI_CITY_TASK,
                meta_pb2.TripSearchCapabilities(
                    is_supported=True,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_IATA_CODES,
                ),
                provider_trips_pb2.SearchTripsRequest(
                    multi_city=provider_trips_pb2.SearchTripsRequest.MultiCity(
                        criteria=[
                            provider_trips_pb2.SearchTripsRequest.Criterion(
                                origin_identifier=_ORIGIN_IATA,
                                destination_identifier=_DESTINATION_IATA,
                                departure_date=_DEPARTURE_DATE,
                            ),
                            provider_trips_pb2.SearchTripsRequest.Criterion(
                                origin_identifier=_DESTINATION_IATA,
                                destination_identifier=_ORIGIN_IATA,
                                departure_date=_RETURN_DATE,
                            ),
                        ],
                    ),
                    passengers=[_REQUEST_PASSENGER],
                ),
                id="multi city with IATA codes identification method",
            ),
            pytest.param(
                _ROUND_TRIP_TASK,
                meta_pb2.TripSearchCapabilities(
                    is_supported=True,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_COORDINATES,
                ),
                provider_trips_pb2.SearchTripsRequest(
                    round_trip=provider_trips_pb2.SearchTripsRequest.RoundTrip(
                        criterion=provider_trips_pb2.SearchTripsRequest.Criterion(
                            origin_coordinates=_ORIGIN_COORDINATES,
                            destination_coordinates=_DESTINATION_COORDINATES,
                            departure_date=_DEPARTURE_DATE,
                        ),
                        return_date=_RETURN_DATE,
                    ),
                    passengers=[_REQUEST_PASSENGER],
                ),
                id="round trip with coordinates identification method",
            ),
            pytest.param(
                _ROUND_TRIP_TASK,
                meta_pb2.TripSearchCapabilities(
                    is_supported=True,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_IATA_CODES,
                ),
                provider_trips_pb2.SearchTripsRequest(
                    round_trip=provider_trips_pb2.SearchTripsRequest.RoundTrip(
                        criterion=provider_trips_pb2.SearchTripsRequest.Criterion(
                            origin_identifier=_ORIGIN_IATA,
                            destination_identifier=_DESTINATION_IATA,
                            departure_date=_DEPARTURE_DATE,
                        ),
                        return_date=_RETURN_DATE,
                    ),
                    passengers=[_REQUEST_PASSENGER],
                ),
                id="round trip with IATA codes identification method",
            ),
        ],
    )
    async def test_generator_is_generating_correct_requests(
        self,
        task: trips_pb2.TripSearchTask,
        capabilities: meta_pb2.TripSearchCapabilities,
        expected: provider_trips_pb2.SearchTripsRequest,
        mocker: plugin.MockerFixture,
    ) -> None:
        providers_list = providers.Collection([])
        mocker.patch.object(
            providers_list,
            "all_healthy",
            _providers_factory(capabilities),
        )

        generator = trips.RequestGenerator(
            providers_list=providers_list,
            stop_resolver=_stop_resolver,
        )

        requests = [request[1] async for request in generator.generate(task)]

        assert len(requests) == 1
        assert json_format.MessageToDict(requests[0]) == json_format.MessageToDict(
            expected,
        )

    @pytest.mark.parametrize(
        ("task", "capabilities"),
        [
            pytest.param(
                _ONE_WAY_TASK,
                meta_pb2.TripSearchCapabilities(
                    is_supported=False,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_COORDINATES,
                ),
                id="one way with unsupported provider",
            ),
            pytest.param(
                _MULTI_CITY_TASK,
                meta_pb2.TripSearchCapabilities(
                    is_supported=False,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_COORDINATES,
                ),
                id="multi city with unsupported provider",
            ),
            pytest.param(
                _ROUND_TRIP_TASK,
                meta_pb2.TripSearchCapabilities(
                    is_supported=False,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_COORDINATES,
                ),
                id="round trip with unsupported provider",
            ),
            pytest.param(
                trips_pb2.TripSearchTask(
                    one_way=trips_pb2.OneWay(
                        criterion=trips_pb2.Criterion(
                            origin=_NO_IATA_IDENTIFIER,
                            destination=_DESTINATION_IDENTIFIER,
                            departure_date=_DEPARTURE_DATE,
                        ),
                    ),
                    passengers=[_TASK_PASSENGER],
                ),
                meta_pb2.TripSearchCapabilities(
                    is_supported=True,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_IATA_CODES,
                ),
                id=(
                    "one way with IATA codes identification method and with stop"
                    " without IATA code"
                ),
            ),
            pytest.param(
                trips_pb2.TripSearchTask(
                    multi_city=trips_pb2.MultiCity(
                        criteria=[
                            trips_pb2.Criterion(
                                origin=_NO_IATA_IDENTIFIER,
                                destination=_DESTINATION_IDENTIFIER,
                                departure_date=_DEPARTURE_DATE,
                            ),
                            trips_pb2.Criterion(
                                origin=_DESTINATION_IDENTIFIER,
                                destination=_NO_IATA_IDENTIFIER,
                                departure_date=_RETURN_DATE,
                            ),
                        ],
                    ),
                    passengers=[_TASK_PASSENGER],
                ),
                meta_pb2.TripSearchCapabilities(
                    is_supported=True,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_IATA_CODES,
                ),
                id=(
                    "multi city with IATA codes identification method and with stop"
                    " without IATA code"
                ),
            ),
            pytest.param(
                trips_pb2.TripSearchTask(
                    round_trip=trips_pb2.RoundTrip(
                        criterion=trips_pb2.Criterion(
                            origin=_NO_IATA_IDENTIFIER,
                            destination=_DESTINATION_IDENTIFIER,
                            departure_date=_DEPARTURE_DATE,
                        ),
                        return_date=_RETURN_DATE,
                    ),
                    passengers=[_TASK_PASSENGER],
                ),
                meta_pb2.TripSearchCapabilities(
                    is_supported=True,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_IATA_CODES,
                ),
                id=(
                    "round trip with IATA codes identification method and with stop"
                    " without IATA code"
                ),
            ),
        ],
    )
    async def test_generator_is_skipping_unsupported_providers(
        self,
        task: trips_pb2.TripSearchTask,
        capabilities: meta_pb2.TripSearchCapabilities,
        mocker: plugin.MockerFixture,
    ) -> None:
        providers_list = providers.Collection([])
        mocker.patch.object(
            providers_list,
            "all_healthy",
            _providers_factory(capabilities),
        )

        generator = trips.RequestGenerator(
            providers_list=providers_list,
            stop_resolver=_stop_resolver,
        )

        requests = [request[1] async for request in generator.generate(task)]

        assert not requests

    @pytest.mark.parametrize(
        ("task", "capabilities"),
        [
            (
                trips_pb2.TripSearchTask(
                    one_way=trips_pb2.OneWay(
                        criterion=trips_pb2.Criterion(
                            origin="invalid",
                            destination=_DESTINATION_IDENTIFIER,
                            departure_date=_DEPARTURE_DATE,
                        ),
                    ),
                    passengers=[_TASK_PASSENGER],
                ),
                meta_pb2.TripSearchCapabilities(
                    is_supported=True,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_COORDINATES,
                ),
            ),
            (
                trips_pb2.TripSearchTask(
                    multi_city=trips_pb2.MultiCity(
                        criteria=[
                            trips_pb2.Criterion(
                                origin="invalid",
                                destination=_DESTINATION_IDENTIFIER,
                                departure_date=_DEPARTURE_DATE,
                            ),
                            trips_pb2.Criterion(
                                origin=_DESTINATION_IDENTIFIER,
                                destination="invalid",
                                departure_date=_RETURN_DATE,
                            ),
                        ],
                    ),
                    passengers=[_TASK_PASSENGER],
                ),
                meta_pb2.TripSearchCapabilities(
                    is_supported=True,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_COORDINATES,
                ),
            ),
            (
                trips_pb2.TripSearchTask(
                    round_trip=trips_pb2.RoundTrip(
                        criterion=trips_pb2.Criterion(
                            origin="invalid",
                            destination=_DESTINATION_IDENTIFIER,
                            departure_date=_DEPARTURE_DATE,
                        ),
                        return_date=_RETURN_DATE,
                    ),
                    passengers=[_TASK_PASSENGER],
                ),
                meta_pb2.TripSearchCapabilities(
                    is_supported=True,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_COORDINATES,
                ),
            ),
        ],
    )
    async def test_generator_is_skipping_invalid_stops(
        self,
        task: trips_pb2.TripSearchTask,
        capabilities: meta_pb2.TripSearchCapabilities,
        mocker: plugin.MockerFixture,
    ) -> None:
        providers_list = providers.Collection([])
        mocker.patch.object(
            providers_list,
            "all_healthy",
            _providers_factory(capabilities),
        )

        generator = trips.RequestGenerator(
            providers_list=providers_list,
            stop_resolver=_stop_resolver,
        )

        requests = [request[1] async for request in generator.generate(task)]

        assert not requests
