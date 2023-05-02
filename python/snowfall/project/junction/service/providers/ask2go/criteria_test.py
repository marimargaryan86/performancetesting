import datetime
from typing import Any, Mapping, Sequence

import freezegun
import more_itertools
import pytest
from google.protobuf import json_format, timestamp_pb2

from snowfall.project.junction.go.service.offers.v1alpha import amqp_pb2, models_pb2
from snowfall.project.junction.service.providers.ask2go import criteria
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import date_pb2, latlng_pb2
from snowfall.stdlib.v1alpha import models_pb2 as common_models_pb2


class _IncrementalTime(object):
    _current = datetime.datetime.now()

    @classmethod
    def get_time(cls) -> timestamp_pb2.Timestamp:
        current = cls._current
        cls._current = current + datetime.timedelta(seconds=1)

        return protobuf.datetime_to_protobuf(current)


_SEARCH_TASK = amqp_pb2.TripOfferSearchTask(
    offer_search_id="SEARCH1",
    search=models_pb2.TripOfferSearch(
        trips=[
            common_models_pb2.Trip(
                id="TRIP1",
                segments=[
                    common_models_pb2.Segment(
                        id="SEGMENT1",
                        legs=[
                            common_models_pb2.Leg(
                                id="LEG1",
                                origin=common_models_pb2.Point(
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=59.351209,
                                        longitude=-2.900537,
                                    ),
                                ),
                                destination=common_models_pb2.Point(
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=59.350376,
                                        longitude=-2.949954,
                                    ),
                                ),
                                departure_at=_IncrementalTime.get_time(),
                                type=common_models_pb2.Schedule.TYPE_AIR,
                            ),
                        ],
                    ),
                ],
            ),
        ],
        passengers=[
            models_pb2.Passenger(
                date_of_birth=date_pb2.Date(
                    year=2000,
                    month=1,
                    day=1,
                ),
            ),
            models_pb2.Passenger(
                date_of_birth=date_pb2.Date(
                    year=2020,
                    month=1,
                    day=1,
                ),
            ),
            models_pb2.Passenger(
                date_of_birth=date_pb2.Date(
                    year=2022,
                    month=1,
                    day=1,
                ),
            ),
        ],
    ),
)

_SEARCH_TASK2 = json_format.ParseDict(
    {
        "offerSearchId": "fdab8109-4bc1-4656-8281-7ca2662fb8c2",
        "search": {
            "trips": [
                {
                    "id": "0367f2c4-df1d-58b6-ae1c-97285083cfbd",
                    "segments": [
                        {
                            "id": "1b35fad6-cded-5afe-8c46-67f1f71a818e",
                            "legs": [
                                {
                                    "id": "f902d6c8-61b2-524a-982e-99faf4723e64",
                                    "origin": {
                                        "ref": "ARN",
                                        "name": "Stockholm-Arlanda Airport",
                                        "coordinates": {
                                            "latitude": 59.650831,
                                            "longitude": 17.92119,
                                        },
                                        "timeZone": "Europe/Stockholm",
                                    },
                                    "destination": {
                                        "ref": "BER",
                                        "name": "Berlin Brandenburg Airport",
                                        "coordinates": {
                                            "latitude": 52.362307,
                                            "longitude": 13.504906,
                                        },
                                        "timeZone": "Europe/Berlin",
                                    },
                                    "departureAt": "2022-11-11T17:15:00Z",
                                    "arrivalAt": "2022-11-11T18:50:00Z",
                                    "type": "TYPE_AIR",
                                    "agencyName": "SK",
                                },
                            ],
                        },
                    ],
                },
            ],
            "passengers": [
                {
                    "dateOfBirth": {
                        "year": 1990,
                        "month": 10,
                        "day": 25,
                    },
                },
            ],
        },
        "sessionToken": "02345678901234567890123256789012",
    },
    amqp_pb2.TripOfferSearchTask(),
)

_SEARCH_TASK3 = json_format.ParseDict(
    {
        "offerSearchId": "a9501e62-9f79-4892-aa9d-58d22289e3a9",
        "search": {
            "trips": [
                {
                    "id": "607af0cb-f642-588b-9e62-3ae7b6e227e0",
                    "segments": [
                        {
                            "id": "746f05a6-3c39-5e58-a590-83dbb3023645",
                            "legs": [
                                {
                                    "id": "0670a78d-3238-5329-a2f4-fd326d0cb082",
                                    "origin": {
                                        "ref": "LHR",
                                        "name": "Heathrow Airport",
                                        "coordinates": {
                                            "latitude": 51.470311,
                                            "longitude": -0.458118,
                                        },
                                        "timeZone": "Europe/London",
                                    },
                                    "destination": {
                                        "ref": "SYD",
                                        "name": "Sydney Airport",
                                        "coordinates": {
                                            "latitude": -33.943011,
                                            "longitude": 151.176138,
                                        },
                                        "timeZone": "Australia/Sydney",
                                    },
                                    "departureAt": "2023-02-20T21:35:00Z",
                                    "arrivalAt": "2023-02-21T19:55:00Z",
                                    "type": "TYPE_AIR",
                                    "agencyName": "BA",
                                },
                            ],
                        },
                    ],
                },
            ],
            "passengers": [
                {
                    "dateOfBirth": {
                        "year": 1990,
                        "month": 10,
                        "day": 25,
                    },
                },
            ],
        },
        "sessionToken": "02345678901234567890123256789012",
    },
    amqp_pb2.TripOfferSearchTask(),
)

_MULTIMODAL_SEARCH_TASK = amqp_pb2.TripOfferSearchTask(
    offer_search_id="MULTIMODAL",
    search=models_pb2.TripOfferSearch(
        trips=[
            common_models_pb2.Trip(
                id="TRIP1",
                segments=[
                    common_models_pb2.Segment(
                        id="SEGMENT1",
                        legs=[
                            common_models_pb2.Leg(
                                id="LEG1",
                                origin=common_models_pb2.Point(
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=59.650831,
                                        longitude=17.92119,
                                    ),
                                ),
                                destination=common_models_pb2.Point(
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=57.667778,
                                        longitude=12.294444,
                                    ),
                                ),
                                departure_at=_IncrementalTime.get_time(),
                                type=common_models_pb2.Schedule.TYPE_AIR,
                            ),
                        ],
                    ),
                    common_models_pb2.Segment(
                        id="SEGMENT2",
                        legs=[
                            common_models_pb2.Leg(
                                id="LEG2",
                                origin=common_models_pb2.Point(
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=57.667778,
                                        longitude=12.294444,
                                    ),
                                ),
                                destination=common_models_pb2.Point(
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=51.470311,
                                        longitude=-0.458118,
                                    ),
                                ),
                                departure_at=_IncrementalTime.get_time(),
                                type=common_models_pb2.Schedule.TYPE_RAIL,
                            ),
                        ],
                    ),
                    common_models_pb2.Segment(
                        id="SEGMENT3",
                        legs=[
                            common_models_pb2.Leg(
                                id="LEG3",
                                origin=common_models_pb2.Point(
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=51.470311,
                                        longitude=-0.458118,
                                    ),
                                ),
                                destination=common_models_pb2.Point(
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=33.9425,
                                        longitude=-118.408056,
                                    ),
                                ),
                                departure_at=_IncrementalTime.get_time(),
                                type=common_models_pb2.Schedule.TYPE_AIR,
                            ),
                        ],
                    ),
                ],
            ),
        ],
        passengers=[
            models_pb2.Passenger(
                date_of_birth=date_pb2.Date(
                    year=2000,
                    month=1,
                    day=1,
                ),
            ),
        ],
    ),
)

_MULTISEGMENT_SEARCH_TASK = amqp_pb2.TripOfferSearchTask(
    offer_search_id="MULTISEGMENT",
    search=models_pb2.TripOfferSearch(
        trips=[
            common_models_pb2.Trip(
                id="TRIP1",
                segments=[
                    common_models_pb2.Segment(
                        id="SEGMENT1",
                        legs=[
                            common_models_pb2.Leg(
                                id="LEG1",
                                origin=common_models_pb2.Point(
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=59.650831,
                                        longitude=17.92119,
                                    ),
                                ),
                                destination=common_models_pb2.Point(
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=57.667778,
                                        longitude=12.294444,
                                    ),
                                ),
                                departure_at=_IncrementalTime.get_time(),
                                type=common_models_pb2.Schedule.TYPE_AIR,
                            ),
                        ],
                    ),
                    common_models_pb2.Segment(
                        id="SEGMENT2",
                        legs=[
                            common_models_pb2.Leg(
                                id="LEG2",
                                origin=common_models_pb2.Point(
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=57.667778,
                                        longitude=12.294444,
                                    ),
                                ),
                                destination=common_models_pb2.Point(
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=51.470311,
                                        longitude=-0.458118,
                                    ),
                                ),
                                departure_at=_IncrementalTime.get_time(),
                                type=common_models_pb2.Schedule.TYPE_AIR,
                            ),
                        ],
                    ),
                ],
            ),
        ],
        passengers=[
            models_pb2.Passenger(
                date_of_birth=date_pb2.Date(
                    year=2000,
                    month=1,
                    day=1,
                ),
            ),
        ],
    ),
)

_ROUNDTRIP_SEARCH_TASK = amqp_pb2.TripOfferSearchTask(
    offer_search_id="ROUNDTRIP",
    search=models_pb2.TripOfferSearch(
        trips=[
            common_models_pb2.Trip(
                id="TRIP1",
                segments=[
                    common_models_pb2.Segment(
                        id="SEGMENT1",
                        legs=[
                            common_models_pb2.Leg(
                                id="LEG1",
                                origin=common_models_pb2.Point(
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=59.650831,
                                        longitude=17.92119,
                                    ),
                                ),
                                destination=common_models_pb2.Point(
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=57.667778,
                                        longitude=12.294444,
                                    ),
                                ),
                                departure_at=_IncrementalTime.get_time(),
                                type=common_models_pb2.Schedule.TYPE_AIR,
                            ),
                        ],
                    ),
                ],
            ),
            common_models_pb2.Trip(
                id="TRIP2",
                segments=[
                    common_models_pb2.Segment(
                        id="SEGMENT2",
                        legs=[
                            common_models_pb2.Leg(
                                id="LEG2",
                                origin=common_models_pb2.Point(
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=57.667778,
                                        longitude=12.294444,
                                    ),
                                ),
                                destination=common_models_pb2.Point(
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=59.650831,
                                        longitude=17.92119,
                                    ),
                                ),
                                departure_at=_IncrementalTime.get_time(),
                                type=common_models_pb2.Schedule.TYPE_AIR,
                            ),
                        ],
                    ),
                ],
            ),
        ],
        passengers=[
            models_pb2.Passenger(
                date_of_birth=date_pb2.Date(
                    year=2000,
                    month=1,
                    day=1,
                ),
            ),
        ],
    ),
)


@pytest.mark.parametrize(
    ("search_task", "expected"),
    [
        (
            _SEARCH_TASK,
            [
                {
                    "origin": "PPW",
                    "destination": "WRY",
                    "outbound_tz": "Europe/London",
                    "inbound_tz": "",
                },
            ],
        ),
        (
            _SEARCH_TASK2,
            [
                {
                    "origin": "ARN",
                    "destination": "BER",
                    "outbound_tz": "Europe/Stockholm",
                    "inbound_tz": "",
                },
            ],
        ),
        (
            _SEARCH_TASK3,
            [
                {
                    "origin": "LHR",
                    "destination": "SYD",
                    "outbound_tz": "Europe/London",
                    "inbound_tz": "",
                },
            ],
        ),
        (
            _MULTIMODAL_SEARCH_TASK,
            [
                {
                    "origin": "ARN",
                    "destination": "GOT",
                    "outbound_tz": "Europe/Stockholm",
                    "inbound_tz": "",
                },
                {
                    "origin": "LHR",
                    "destination": "LAX",
                    "outbound_tz": "Europe/London",
                    "inbound_tz": "",
                },
            ],
        ),
        (
            _MULTISEGMENT_SEARCH_TASK,
            [
                {
                    "origin": "ARN",
                    "destination": "LHR",
                    "outbound_tz": "Europe/Stockholm",
                    "inbound_tz": "",
                },
            ],
        ),
        (
            _ROUNDTRIP_SEARCH_TASK,
            [
                {
                    "origin": "ARN",
                    "destination": "GOT",
                    "outbound_tz": "Europe/Stockholm",
                    "inbound_tz": "",
                },
                {
                    "origin": "GOT",
                    "destination": "ARN",
                    "outbound_tz": "Europe/Stockholm",
                    "inbound_tz": "",
                },
                {
                    "origin": "ARN",
                    "destination": "GOT",
                    "outbound_tz": "Europe/Stockholm",
                    "inbound_tz": "Europe/Stockholm",
                },
            ],
        ),
    ],
)
def test_criteria_with_expected_pairs_are_generated(
    criteria_generator: criteria.CriteriaGenerator,
    search_task: amqp_pb2.TripOfferSearchTask,
    expected: Sequence[Mapping[str, Any]],
) -> None:
    search_tasks = list(criteria_generator.from_search(search=search_task.search))
    search_task_pairs = [
        {
            "origin": search_task.criteria.origin_iata,
            "destination": search_task.criteria.destination_iata,
            "outbound_tz": search_task.criteria.outbound_departure.time_zone.id,
            "inbound_tz": search_task.criteria.inbound_departure.time_zone.id,
        }
        for search_task in search_tasks
    ]

    for expected_pair in expected:
        assert expected_pair in search_task_pairs

    for search_task_pair in search_task_pairs:
        assert search_task_pair in expected


@pytest.mark.parametrize(
    ("search_task", "expected"),
    [
        (
            _SEARCH_TASK,
            {
                "adults": 1,
                "children": 1,
                "infants": 1,
            },
        ),
        (
            _SEARCH_TASK2,
            {
                "adults": 1,
                "children": 0,
                "infants": 0,
            },
        ),
        (
            _SEARCH_TASK3,
            {
                "adults": 1,
                "children": 0,
                "infants": 0,
            },
        ),
    ],
)
@freezegun.freeze_time("2022-04-01")
def test_criteria_with_expected_passengers_are_generated(
    criteria_generator: criteria.CriteriaGenerator,
    search_task: amqp_pb2.TripOfferSearchTask,
    expected: Mapping[str, int],
) -> None:
    search_tasks = list(criteria_generator.from_search(search=search_task.search))
    first_search_task = more_itertools.first(search_tasks, None)
    assert first_search_task
    assert first_search_task.criteria.adults == expected["adults"]
    assert first_search_task.criteria.children == expected["children"]
    assert first_search_task.criteria.infants == expected["infants"]
