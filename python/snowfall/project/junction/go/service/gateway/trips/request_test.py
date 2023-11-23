import datetime
from collections.abc import AsyncIterable, Callable, Sequence

import pytest
from google.protobuf import json_format
from grpc import aio
from pytest_mock import plugin

from snowfall.project.junction.go.service.gateway import providers, stops
from snowfall.project.junction.go.service.gateway.trips import request as trips_request
from snowfall.project.junction.go.service.gateway.v1 import trips_pb2
from snowfall.project.junction.go.service.places.v1 import models_pb2
from snowfall.project.junction.provider.v2alpha import meta_pb2
from snowfall.project.junction.provider.v2alpha import trips_pb2 as provider_trips_pb2
from snowfall.project.junction.v1 import passenger_type_pb2, segment_type_pb2
from snowfall.stdlib import string
from snowfall.stdlib.v1 import date_pb2, latlng_pb2

_ORIGIN_IDENTIFIER = "foobar"
_ORIGIN_IATA = "FOO"
_DESTINATION_IDENTIFIER = "bazqux"
_DESTINATION_IATA = "BAZ"
_NO_IATA_IDENTIFIER = "no_iata"
_DEPARTURE_DATE = date_pb2.Date(year=2023, month=10, day=25)
_RETURN_DATE = date_pb2.Date(year=2023, month=11, day=25)
_PASSENGER_ID = string.uuid()
_ORIGIN_COORDINATES = latlng_pb2.LatLng(
    latitude=1,
    longitude=1,
)
_DESTINATION_COORDINATES = latlng_pb2.LatLng(
    latitude=-1,
    longitude=-1,
)
_TASK_PASSENGER = trips_pb2.Passenger(
    type=passenger_type_pb2.PASSENGER_TYPE_ADULT,
)
_REQUEST_PASSENGER = provider_trips_pb2.SearchTripsRequest.Passenger(
    id=_PASSENGER_ID,
    date_of_birth=date_pb2.Date(
        year=datetime.datetime.now(tz=datetime.UTC).today().year - 30,
        month=1,
        day=1,
    ),
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
_ONE_WAY_TASK_WITH_AIR_SEGMENT = trips_pb2.TripSearchTask(
    one_way=trips_pb2.OneWay(
        criterion=trips_pb2.Criterion(
            origin=_ORIGIN_IDENTIFIER,
            destination=_DESTINATION_IDENTIFIER,
            departure_date=_DEPARTURE_DATE,
            segment_types=[segment_type_pb2.SEGMENT_TYPE_FLIGHT],
        ),
    ),
    passengers=[_TASK_PASSENGER],
)
_MULTI_CITY_TASK_WITH_AIR_AND_BUS_SEGMENT = trips_pb2.TripSearchTask(
    multi_city=trips_pb2.MultiCity(
        criteria=[
            trips_pb2.Criterion(
                origin=_ORIGIN_IDENTIFIER,
                destination=_DESTINATION_IDENTIFIER,
                departure_date=_DEPARTURE_DATE,
                segment_types=[segment_type_pb2.SEGMENT_TYPE_FLIGHT],
            ),
            trips_pb2.Criterion(
                origin=_DESTINATION_IDENTIFIER,
                destination=_ORIGIN_IDENTIFIER,
                departure_date=_RETURN_DATE,
                segment_types=[segment_type_pb2.SEGMENT_TYPE_BUS],
            ),
        ],
    ),
    passengers=[_TASK_PASSENGER],
)
_ROUND_TRIP_TASK_WITH_AIR_SEGMENT = trips_pb2.TripSearchTask(
    round_trip=trips_pb2.RoundTrip(
        criterion=trips_pb2.Criterion(
            origin=_ORIGIN_IDENTIFIER,
            destination=_DESTINATION_IDENTIFIER,
            departure_date=_DEPARTURE_DATE,
            segment_types=[segment_type_pb2.SEGMENT_TYPE_FLIGHT],
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
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
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
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
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
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
                    supports_multi_city=True,
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
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
                    supports_multi_city=True,
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
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
                    supports_round_trip=True,
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
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
                    supports_round_trip=True,
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
            pytest.param(
                _ONE_WAY_TASK_WITH_AIR_SEGMENT,
                meta_pb2.TripSearchCapabilities(
                    is_supported=True,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_COORDINATES,
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
                    supported_segment_types=[
                        segment_type_pb2.SegmentType.SEGMENT_TYPE_FLIGHT,
                    ],
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
                id=(
                    "one way with coordinates identification method and air segment"
                    " type"
                ),
            ),
            pytest.param(
                _MULTI_CITY_TASK_WITH_AIR_AND_BUS_SEGMENT,
                meta_pb2.TripSearchCapabilities(
                    is_supported=True,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_COORDINATES,
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
                    supported_segment_types=[
                        segment_type_pb2.SegmentType.SEGMENT_TYPE_FLIGHT,
                        segment_type_pb2.SegmentType.SEGMENT_TYPE_BUS,
                    ],
                    supports_multi_city=True,
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
                id=(
                    "multi city with coordinates identification method and air and bus"
                    " segment types"
                ),
            ),
            pytest.param(
                _ROUND_TRIP_TASK_WITH_AIR_SEGMENT,
                meta_pb2.TripSearchCapabilities(
                    is_supported=True,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_COORDINATES,
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
                    supported_segment_types=[
                        segment_type_pb2.SegmentType.SEGMENT_TYPE_FLIGHT,
                    ],
                    supports_round_trip=True,
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
                id=(
                    "round trip with coordinates identification method and air segment"
                    " type"
                ),
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
        mocker.patch("snowfall.stdlib.string.uuid", return_value=_PASSENGER_ID)
        mocker.patch.object(
            providers_list,
            "all_healthy",
            _providers_factory(capabilities),
        )

        generator = trips_request.Generator(
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
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
                ),
                id="one way with unsupported provider",
            ),
            pytest.param(
                _MULTI_CITY_TASK,
                meta_pb2.TripSearchCapabilities(
                    is_supported=False,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_COORDINATES,
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
                ),
                id="multi city with unsupported provider",
            ),
            pytest.param(
                _ROUND_TRIP_TASK,
                meta_pb2.TripSearchCapabilities(
                    is_supported=False,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_COORDINATES,
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
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
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
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
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
                    supports_multi_city=True,
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
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
                    supports_round_trip=True,
                ),
                id=(
                    "round trip with IATA codes identification method and with stop"
                    " without IATA code"
                ),
            ),
            pytest.param(
                _ONE_WAY_TASK_WITH_AIR_SEGMENT,
                meta_pb2.TripSearchCapabilities(
                    is_supported=True,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_COORDINATES,
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
                    supported_segment_types=[
                        segment_type_pb2.SegmentType.SEGMENT_TYPE_BUS,
                    ],
                ),
                id="one way with unsupported segment type",
            ),
            pytest.param(
                _MULTI_CITY_TASK_WITH_AIR_AND_BUS_SEGMENT,
                meta_pb2.TripSearchCapabilities(
                    is_supported=True,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_COORDINATES,
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
                    supported_segment_types=[
                        segment_type_pb2.SegmentType.SEGMENT_TYPE_FLIGHT,
                        segment_type_pb2.SegmentType.SEGMENT_TYPE_TRAIN,
                    ],
                    supports_multi_city=True,
                ),
                id="multi city with one supported and one unsupported segment type",
            ),
            pytest.param(
                _ROUND_TRIP_TASK_WITH_AIR_SEGMENT,
                meta_pb2.TripSearchCapabilities(
                    is_supported=True,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_COORDINATES,
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
                    supported_segment_types=[
                        segment_type_pb2.SegmentType.SEGMENT_TYPE_BUS,
                    ],
                    supports_round_trip=True,
                ),
                id="round trip with unsupported segment type",
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
        mocker.patch("snowfall.stdlib.string.uuid", return_value=_PASSENGER_ID)
        mocker.patch.object(
            providers_list,
            "all_healthy",
            _providers_factory(capabilities),
        )

        generator = trips_request.Generator(
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
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
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
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
                    supports_multi_city=True,
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
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
                    supports_round_trip=True,
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
        mocker.patch("snowfall.stdlib.string.uuid", return_value=_PASSENGER_ID)
        mocker.patch.object(
            providers_list,
            "all_healthy",
            _providers_factory(capabilities),
        )

        generator = trips_request.Generator(
            providers_list=providers_list,
            stop_resolver=_stop_resolver,
        )

        requests = [request[1] async for request in generator.generate(task)]

        assert not requests

    @pytest.mark.parametrize(
        ("task", "capabilities", "expected"),
        [
            pytest.param(
                _MULTI_CITY_TASK,
                meta_pb2.TripSearchCapabilities(
                    is_supported=True,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_COORDINATES,
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
                    supports_multi_city=False,
                ),
                [
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
                    provider_trips_pb2.SearchTripsRequest(
                        one_way=provider_trips_pb2.SearchTripsRequest.OneWay(
                            criterion=provider_trips_pb2.SearchTripsRequest.Criterion(
                                origin_coordinates=_DESTINATION_COORDINATES,
                                destination_coordinates=_ORIGIN_COORDINATES,
                                departure_date=_RETURN_DATE,
                            ),
                        ),
                        passengers=[_REQUEST_PASSENGER],
                    ),
                ],
                id="multi city should fall back to one one way per trip if unsupported",
            ),
            pytest.param(
                _ROUND_TRIP_TASK,
                meta_pb2.TripSearchCapabilities(
                    is_supported=True,
                    stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_COORDINATES,
                    passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
                    supports_round_trip=False,
                ),
                [
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
                    provider_trips_pb2.SearchTripsRequest(
                        one_way=provider_trips_pb2.SearchTripsRequest.OneWay(
                            criterion=provider_trips_pb2.SearchTripsRequest.Criterion(
                                origin_coordinates=_DESTINATION_COORDINATES,
                                destination_coordinates=_ORIGIN_COORDINATES,
                                departure_date=_RETURN_DATE,
                            ),
                        ),
                        passengers=[_REQUEST_PASSENGER],
                    ),
                ],
                id="round trip should fall back to two one ways if unsupported",
            ),
        ],
    )
    async def test_generator_can_fallback_to_one_way(
        self,
        task: trips_pb2.TripSearchTask,
        capabilities: meta_pb2.TripSearchCapabilities,
        expected: Sequence[provider_trips_pb2.SearchTripsRequest],
        mocker: plugin.MockerFixture,
    ) -> None:
        providers_list = providers.Collection([])
        mocker.patch("snowfall.stdlib.string.uuid", return_value=_PASSENGER_ID)
        mocker.patch.object(
            providers_list,
            "all_healthy",
            _providers_factory(capabilities),
        )

        generator = trips_request.Generator(
            providers_list=providers_list,
            stop_resolver=_stop_resolver,
        )

        requests = [request[1] async for request in generator.generate(task)]

        assert len(requests) == len(expected)
        assert all(
            json_format.MessageToDict(requests[idx])
            == json_format.MessageToDict(expected[idx])
            for idx in range(len(expected))
        )
