import datetime
from typing import Mapping, Sequence

import freezegun
import more_itertools
import pytest

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.offers.v1alpha import offers_pb2
from snowfall.junction.providers.ask2go import criteria
from snowfall.stdlib.format import protobuf

_SEARCH_TASK = offers_pb2.TripOfferSearchTask(
    offer_search_id="SEARCH1",
    search=offers_pb2.TripOfferSearch(
        segments=[
            models_pb2.Segment(
                id="SEGMENT1",
                legs=[
                    models_pb2.Leg(
                        id="LEG1",
                        origin=models_pb2.Point(
                            coordinates=models_pb2.Coordinates(
                                latitude=59.351209,
                                longitude=-2.900537,
                            ),
                        ),
                        destination=models_pb2.Point(
                            coordinates=models_pb2.Coordinates(
                                latitude=59.350376,
                                longitude=-2.949954,
                            ),
                        ),
                        departure_at=protobuf.datetime_to_protobuf(
                            datetime.datetime.now(),
                        ),
                        type=models_pb2.Schedule.TYPE_AIR,
                    ),
                ],
            ),
        ],
        passengers=[
            offers_pb2.Passenger(
                date_of_birth=models_pb2.Date(
                    year=2000,
                    month=1,
                    day=1,
                ),
            ),
            offers_pb2.Passenger(
                date_of_birth=models_pb2.Date(
                    year=2020,
                    month=1,
                    day=1,
                ),
            ),
            offers_pb2.Passenger(
                date_of_birth=models_pb2.Date(
                    year=2022,
                    month=1,
                    day=1,
                ),
            ),
        ],
    ),
)


@pytest.mark.parametrize(
    "search_task, expected",
    [
        (
            _SEARCH_TASK,
            [
                ("PPW", "WRY"),
            ],
        ),
    ],
)
def test_criteria_with_expected_pairs_are_generated(
    criteria_generator: criteria.CriteriaGenerator,
    search_task: offers_pb2.TripOfferSearchTask,
    expected: Sequence[Sequence[str]],
) -> None:
    search_tasks = list(criteria_generator.from_search_task(search_task=search_task))
    assert len(search_tasks) == len(expected)

    search_task_pairs = [
        (search_task.criteria.origin_iata, search_task.criteria.destination_iata)
        for search_task in search_tasks
    ]

    for pair in expected:
        assert pair in search_task_pairs


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
    ],
)
@freezegun.freeze_time("2022-04-01")
def test_criteria_with_expected_passengers_are_generated(
    criteria_generator: criteria.CriteriaGenerator,
    search_task: offers_pb2.TripOfferSearchTask,
    expected: Mapping[str, int],
) -> None:
    search_tasks = list(criteria_generator.from_search_task(search_task=search_task))
    first_search_task = more_itertools.first(search_tasks)

    assert first_search_task.criteria.adults == expected["adults"]
    assert first_search_task.criteria.children == expected["children"]
    assert first_search_task.criteria.infants == expected["infants"]
