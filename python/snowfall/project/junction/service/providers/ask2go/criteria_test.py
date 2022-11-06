import base64
import datetime
from typing import Any, Mapping, Sequence

import freezegun
import more_itertools
import pytest

from snowfall.project.junction.service.offers.v1alpha import amqp_pb2, models_pb2
from snowfall.project.junction.service.providers.ask2go import criteria
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import models_pb2 as common_models_pb2

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
                                    coordinates=common_models_pb2.Coordinates(
                                        latitude=59.351209,
                                        longitude=-2.900537,
                                    ),
                                ),
                                destination=common_models_pb2.Point(
                                    coordinates=common_models_pb2.Coordinates(
                                        latitude=59.350376,
                                        longitude=-2.949954,
                                    ),
                                ),
                                departure_at=protobuf.datetime_to_protobuf(
                                    datetime.datetime.now(),
                                ),
                                type=common_models_pb2.Schedule.TYPE_AIR,
                            ),
                        ],
                    ),
                ],
            ),
        ],
        passengers=[
            models_pb2.Passenger(
                date_of_birth=common_models_pb2.Date(
                    year=2000,
                    month=1,
                    day=1,
                ),
            ),
            models_pb2.Passenger(
                date_of_birth=common_models_pb2.Date(
                    year=2020,
                    month=1,
                    day=1,
                ),
            ),
            models_pb2.Passenger(
                date_of_birth=common_models_pb2.Date(
                    year=2022,
                    month=1,
                    day=1,
                ),
            ),
        ],
    ),
)

# SK - 2022-11-11 - ARN -> BER - 18:15:00 -> 19:50:00 - 1 ADULT
_SEARCH_TASK2_ENCODED = """
Clh0eXBlLmdvb2dsZWFwaXMuY29tL3Nub3dmYWxsLnByb2plY3QuanVuY3Rpb24uc2VydmljZS5vZmZlcnMudjFh
bHBoYS5UcmlwT2ZmZXJTZWFyY2hUYXNrEvUCCiRmZGFiODEwOS00YmMxLTQ2NTYtODI4MS03Y2EyNjYyZmI4YzIS
qgIKnAIKJDAzNjdmMmM0LWRmMWQtNThiNi1hZTFjLTk3Mjg1MDgzY2ZiZBLzAQokMWIzNWZhZDYtY2RlZC01YWZl
LThjNDYtNjdmMWY3MWE4MThlEsoBCiRmOTAyZDZjOC02MWIyLTUyNGEtOTgyZS05OWZhZjQ3MjNlNjQSRgoDQVJO
EhlTdG9ja2hvbG0tQXJsYW5kYSBBaXJwb3J0GhIJihwibk7TTUAR+WabG9PrMUAiEEV1cm9wZS9TdG9ja2hvbG0a
RAoDQkVSEhpCZXJsaW4gQnJhbmRlbmJ1cmcgQWlycG9ydBoSCVIOZhNgLkpAEb0bCwqDAitAIg1FdXJvcGUvQmVy
bGluIgYIlIa6mwYqBgjYsrqbBjABOgJTSxIJCgcIxg8QChgZGiAwMjM0NTY3ODkwMTIzNDU2Nzg5MDEyMzI1Njc4
OTAxMg==
"""
_SEARCH_TASK2 = protobuf.AnySerializer[amqp_pb2.TripOfferSearchTask].deserialize(
    base64.b64decode(_SEARCH_TASK2_ENCODED),
)

# BA - 2023-02-20 - LHR -> SIN -> SYD - 21:35:00 -> 06:55:00 - 1 ADULT
_SEARCH_TASK3_ENCODED = """
Clh0eXBlLmdvb2dsZWFwaXMuY29tL3Nub3dmYWxsLnByb2plY3QuanVuY3Rpb24uc2VydmljZS5vZmZlcnMudjFh
bHBoYS5UcmlwT2ZmZXJTZWFyY2hUYXNrEuACCiRhOTUwMWU2Mi05Zjc5LTQ4OTItYWE5ZC01OGQyMjI4OWUzYTkS
lQIKhwIKJDYwN2FmMGNiLWY2NDItNTg4Yi05ZTYyLTNhZTdiNmUyMjdlMBLeAQokNzQ2ZjA1YTYtM2MzOS01ZTU4
LWE1OTAtODNkYmIzMDIzNjQ1ErUBCiQwNjcwYTc4ZC0zMjM4LTUzMjktYTJmNC1mZDMyNmQwY2IwODISOgoDTEhS
EhBIZWF0aHJvdyBBaXJwb3J0GhIJe/mdJjO8SUARFF/tKM5R3b8iDUV1cm9wZS9Mb25kb24aOwoDU1lEEg5TeWRu
ZXkgQWlycG9ydBoSCVZinpW0+EDAEaeyKOyi5WJAIhBBdXN0cmFsaWEvU3lkbmV5IgYIhM/PnwYqBgiUw9SfBjAB
OgJCQRIJCgcIxg8QChgZGiAwMjM0NTY3ODkwMTIzNDU2Nzg5MDEyMzI1Njc4OTAxMg==
"""
_SEARCH_TASK3 = protobuf.AnySerializer[amqp_pb2.TripOfferSearchTask].deserialize(
    base64.b64decode(_SEARCH_TASK3_ENCODED),
)

_MULTIMODAL_SEARCH_TASK = amqp_pb2.TripOfferSearchTask(
    offer_search_id="SEARCH4",
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
                                    coordinates=common_models_pb2.Coordinates(
                                        latitude=59.650831,
                                        longitude=17.92119,
                                    ),
                                ),
                                destination=common_models_pb2.Point(
                                    coordinates=common_models_pb2.Coordinates(
                                        latitude=57.667778,
                                        longitude=12.294444,
                                    ),
                                ),
                                departure_at=protobuf.datetime_to_protobuf(
                                    datetime.datetime.now(),
                                ),
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
                                    coordinates=common_models_pb2.Coordinates(
                                        latitude=57.667778,
                                        longitude=12.294444,
                                    ),
                                ),
                                destination=common_models_pb2.Point(
                                    coordinates=common_models_pb2.Coordinates(
                                        latitude=51.470311,
                                        longitude=-0.458118,
                                    ),
                                ),
                                departure_at=protobuf.datetime_to_protobuf(
                                    datetime.datetime.now(),
                                ),
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
                                    coordinates=common_models_pb2.Coordinates(
                                        latitude=51.470311,
                                        longitude=-0.458118,
                                    ),
                                ),
                                destination=common_models_pb2.Point(
                                    coordinates=common_models_pb2.Coordinates(
                                        latitude=33.9425,
                                        longitude=-118.408056,
                                    ),
                                ),
                                departure_at=protobuf.datetime_to_protobuf(
                                    datetime.datetime.now(),
                                ),
                                type=common_models_pb2.Schedule.TYPE_AIR,
                            ),
                        ],
                    ),
                ],
            ),
        ],
        passengers=[
            models_pb2.Passenger(
                date_of_birth=common_models_pb2.Date(
                    year=2000,
                    month=1,
                    day=1,
                ),
            ),
        ],
    ),
)

_MULTISEGMENT_SEARCH_TASK = amqp_pb2.TripOfferSearchTask(
    offer_search_id="SEARCH5",
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
                                    coordinates=common_models_pb2.Coordinates(
                                        latitude=59.650831,
                                        longitude=17.92119,
                                    ),
                                ),
                                destination=common_models_pb2.Point(
                                    coordinates=common_models_pb2.Coordinates(
                                        latitude=57.667778,
                                        longitude=12.294444,
                                    ),
                                ),
                                departure_at=protobuf.datetime_to_protobuf(
                                    datetime.datetime.now(),
                                ),
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
                                    coordinates=common_models_pb2.Coordinates(
                                        latitude=57.667778,
                                        longitude=12.294444,
                                    ),
                                ),
                                destination=common_models_pb2.Point(
                                    coordinates=common_models_pb2.Coordinates(
                                        latitude=51.470311,
                                        longitude=-0.458118,
                                    ),
                                ),
                                departure_at=protobuf.datetime_to_protobuf(
                                    datetime.datetime.now(),
                                ),
                                type=common_models_pb2.Schedule.TYPE_AIR,
                            ),
                        ],
                    ),
                ],
            ),
        ],
        passengers=[
            models_pb2.Passenger(
                date_of_birth=common_models_pb2.Date(
                    year=2000,
                    month=1,
                    day=1,
                ),
            ),
        ],
    ),
)

_ROUNDTRIP_SEARCH_TASK = amqp_pb2.TripOfferSearchTask(
    offer_search_id="SEARCH6",
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
                                    coordinates=common_models_pb2.Coordinates(
                                        latitude=59.650831,
                                        longitude=17.92119,
                                    ),
                                ),
                                destination=common_models_pb2.Point(
                                    coordinates=common_models_pb2.Coordinates(
                                        latitude=57.667778,
                                        longitude=12.294444,
                                    ),
                                ),
                                departure_at=protobuf.datetime_to_protobuf(
                                    datetime.datetime.now(),
                                ),
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
                                    coordinates=common_models_pb2.Coordinates(
                                        latitude=57.667778,
                                        longitude=12.294444,
                                    ),
                                ),
                                destination=common_models_pb2.Point(
                                    coordinates=common_models_pb2.Coordinates(
                                        latitude=59.650831,
                                        longitude=17.92119,
                                    ),
                                ),
                                departure_at=protobuf.datetime_to_protobuf(
                                    datetime.datetime.now(),
                                ),
                                type=common_models_pb2.Schedule.TYPE_AIR,
                            ),
                        ],
                    ),
                ],
            ),
        ],
        passengers=[
            models_pb2.Passenger(
                date_of_birth=common_models_pb2.Date(
                    year=2000,
                    month=1,
                    day=1,
                ),
            ),
        ],
    ),
)


@pytest.mark.parametrize(
    "search_task, expected, skipped",
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
            False,
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
            False,
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
            False,
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
            False,
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
            True,
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
            False,
        ),
    ],
)
def test_criteria_with_expected_pairs_are_generated(
    criteria_generator: criteria.CriteriaGenerator,
    search_task: amqp_pb2.TripOfferSearchTask,
    expected: Sequence[Mapping[str, Any]],
    skipped: bool,
) -> None:
    if skipped:
        pytest.skip("Not supported yet")

    search_tasks = list(criteria_generator.from_search_task(search_task=search_task))
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
    "search_task, expected",
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
    search_tasks = list(criteria_generator.from_search_task(search_task=search_task))
    first_search_task = more_itertools.first(search_tasks)

    assert first_search_task.criteria.adults == expected["adults"]
    assert first_search_task.criteria.children == expected["children"]
    assert first_search_task.criteria.infants == expected["infants"]
