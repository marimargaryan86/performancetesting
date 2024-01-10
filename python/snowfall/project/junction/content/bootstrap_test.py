import uuid
from collections.abc import Iterable
from typing import Any

import pytest

from snowfall.project.junction.content import bootstrap, meta, trips
from snowfall.project.junction.provider.v2alpha import meta_pb2, trips_pb2
from snowfall.project.junction.v1 import segment_type_pb2

_PROVIDER_ID = uuid.uuid4()
_PROVIDER_NAME = "Foo"


async def _mock_one_way_implementation(
    trip_request: trips_pb2.SearchTripsRequest.OneWay,
    passengers: Iterable[trips_pb2.SearchTripsRequest.Passenger],
) -> trips_pb2.SearchTripsResponse:
    return trips_pb2.SearchTripsResponse()


def test_only_meta_is_created() -> None:
    services = bootstrap.create_grpc_services(
        bootstrap.ProviderConfiguration(
            provider_id=_PROVIDER_ID,
            provider_name=_PROVIDER_NAME,
        ),
    )

    assert _instance_in_list(meta.MetaService, services)


@pytest.mark.parametrize(
    "trip_search_implementation",
    [
        trips.TripSearchImplementation(
            passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_UNSPECIFIED,
            stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_PROVIDER_IDS,
            supported_segment_types=[segment_type_pb2.SEGMENT_TYPE_FLIGHT],
            one_way=_mock_one_way_implementation,
        ),
        trips.TripSearchImplementation(
            passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
            stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_UNSPECIFIED,
            supported_segment_types=[segment_type_pb2.SEGMENT_TYPE_FLIGHT],
            one_way=_mock_one_way_implementation,
        ),
        trips.TripSearchImplementation(
            passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
            stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_PROVIDER_IDS,
            supported_segment_types=[],
            one_way=_mock_one_way_implementation,
        ),
        trips.TripSearchImplementation(
            passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
            stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_PROVIDER_IDS,
            supported_segment_types=[segment_type_pb2.SEGMENT_TYPE_UNSPECIFIED],
            one_way=_mock_one_way_implementation,
        ),
    ],
)
def test_creation_fails_when_trip_search_is_misconfigured(
    trip_search_implementation: trips.TripSearchImplementation,
) -> None:
    with pytest.raises(bootstrap.ConfigurationError):
        bootstrap.create_grpc_services(
            bootstrap.ProviderConfiguration(
                provider_id=_PROVIDER_ID,
                provider_name=_PROVIDER_NAME,
                trip_search_implementation=trip_search_implementation,
            ),
        )


def test_trip_service_is_created() -> None:
    services = bootstrap.create_grpc_services(
        bootstrap.ProviderConfiguration(
            provider_id=_PROVIDER_ID,
            provider_name=_PROVIDER_NAME,
            trip_search_implementation=trips.TripSearchImplementation(
                passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
                stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_PROVIDER_IDS,
                supported_segment_types=[segment_type_pb2.SEGMENT_TYPE_FLIGHT],
                one_way=_mock_one_way_implementation,
            ),
        ),
    )

    assert _instance_in_list(trips.TripService, services)


def _instance_in_list(instance: type, services: Iterable[Any]) -> bool:
    return any(isinstance(service, instance) for service in services)
