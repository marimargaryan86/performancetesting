import datetime
import zoneinfo
from collections.abc import Iterable, Mapping, Sequence
from typing import Any
from unittest import mock

import pytest

from snowfall.project.junction.go.v1 import models_pb2
from snowfall.project.junction.provider import segment_grouper
from snowfall.stdlib import h3


class _IncrementalTime:
    _current = datetime.datetime.now(tz=datetime.UTC)

    @classmethod
    def get_time(cls) -> datetime.datetime:
        current = cls._current
        cls._current = current + datetime.timedelta(seconds=1)

        return current


@pytest.fixture()
def h3_mapping() -> h3.H3MappingRepository[h3.MappedValue]:
    stub = mock.create_autospec(h3.H3MappingRepository)
    mocked_value = h3.CoordinatesItem(
        identifier="foo",
        longitude=0,
        latitude=0,
        timezone=zoneinfo.ZoneInfo("Europe/Stockholm"),
    )
    stub.find_mapped_values = mock.Mock(return_value={mocked_value})

    return stub


@pytest.fixture()
def grouper(
    h3_mapping: h3.H3MappingRepository[h3.MappedValue],
) -> segment_grouper.SegmentGrouper[h3.MappedValue]:
    return segment_grouper.SegmentGrouper(h3_mapping)


@pytest.fixture()
def roundtrip() -> list[segment_grouper.SubTrip]:
    return [
        segment_grouper.SubTrip(
            trip_id="foo",
            origins=frozenset(("ARN",)),
            destinations=frozenset(("LHR",)),
            departure=_IncrementalTime.get_time(),
            arrival=_IncrementalTime.get_time(),
            segments=[],
        ),
        segment_grouper.SubTrip(
            trip_id="bar",
            origins=frozenset(("LHR",)),
            destinations=frozenset(("ARN",)),
            departure=_IncrementalTime.get_time(),
            arrival=_IncrementalTime.get_time(),
            segments=[],
        ),
    ]


def _generate_trips(
    trips: Iterable[Iterable[models_pb2.Schedule.Type.ValueType]],
) -> list[models_pb2.Trip]:
    return [
        models_pb2.Trip(
            id=str(idx),
            segments=[
                models_pb2.Segment(legs=[models_pb2.Leg(type=segment)])
                for segment in segments
            ],
        )
        for idx, segments in enumerate(trips)
    ]


@pytest.mark.parametrize(
    ("trips", "expected"),
    [
        (_generate_trips([[models_pb2.Schedule.TYPE_RAIL]]), 0),
        (
            _generate_trips(
                [
                    [
                        models_pb2.Schedule.TYPE_AIR,
                        models_pb2.Schedule.TYPE_RAIL,
                        models_pb2.Schedule.TYPE_AIR,
                    ],
                ],
            ),
            2,
        ),
        (
            _generate_trips(
                [
                    [
                        models_pb2.Schedule.TYPE_AIR,
                        models_pb2.Schedule.TYPE_RAIL,
                        models_pb2.Schedule.TYPE_AIR,
                        models_pb2.Schedule.TYPE_RAIL,
                    ],
                ],
            ),
            2,
        ),
        (
            _generate_trips(
                [
                    [
                        models_pb2.Schedule.TYPE_AIR,
                        models_pb2.Schedule.TYPE_AIR,
                    ],
                    [
                        models_pb2.Schedule.TYPE_AIR,
                        models_pb2.Schedule.TYPE_AIR,
                    ],
                ],
            ),
            2,
        ),
    ],
)
def test_trips_are_broken_into_sub_trips(
    grouper: segment_grouper.SegmentGrouper[h3.MappedValue],
    trips: Iterable[models_pb2.Trip],
    expected: int,
) -> None:
    sub_trips = grouper.trips_to_sub_trips(
        trips=trips,
        type_filter=models_pb2.Schedule.TYPE_AIR,
    )
    assert len(list(sub_trips)) == expected


@pytest.mark.parametrize(
    ("trips", "expected_segments_count"),
    [
        (_generate_trips([[models_pb2.Schedule.TYPE_RAIL]]), []),
        (
            _generate_trips(
                [
                    [
                        models_pb2.Schedule.TYPE_AIR,
                        models_pb2.Schedule.TYPE_RAIL,
                        models_pb2.Schedule.TYPE_AIR,
                        models_pb2.Schedule.TYPE_RAIL,
                        models_pb2.Schedule.TYPE_AIR,
                        models_pb2.Schedule.TYPE_AIR,
                        models_pb2.Schedule.TYPE_AIR,
                        models_pb2.Schedule.TYPE_RAIL,
                    ],
                ],
            ),
            [1, 1, 3],
        ),
        (
            _generate_trips(
                [
                    [
                        models_pb2.Schedule.TYPE_AIR,
                        models_pb2.Schedule.TYPE_AIR,
                        models_pb2.Schedule.TYPE_RAIL,
                        models_pb2.Schedule.TYPE_AIR,
                    ],
                    [
                        models_pb2.Schedule.TYPE_AIR,
                        models_pb2.Schedule.TYPE_AIR,
                    ],
                ],
            ),
            [2, 1, 2],
        ),
    ],
)
def test_sub_trips_segments_count(
    grouper: segment_grouper.SegmentGrouper[h3.MappedValue],
    trips: Iterable[models_pb2.Trip],
    expected_segments_count: Sequence[int],
) -> None:
    sub_trips = grouper.trips_to_sub_trips(
        trips=trips,
        type_filter=models_pb2.Schedule.TYPE_AIR,
    )

    for sub_trip_index, sub_trip in enumerate(list(sub_trips)):
        assert len(sub_trip.segments) == expected_segments_count[sub_trip_index]


@pytest.mark.parametrize(
    ("sub_trips", "expected"),
    [
        (
            [
                {
                    "id": "foo",
                    "org": {"ARN"},
                    "dest": {"LHR"},
                },
            ],
            1,
        ),
        (
            [
                {
                    "id": "foo",
                    "org": {"GOT"},
                    "dest": {"ARN"},
                },
                {
                    "id": "foo",
                    "org": {"LHR"},
                    "dest": {"LAX"},
                },
            ],
            2,
        ),
        (
            [
                {
                    "id": "foo",
                    "org": {"GOT"},
                    "dest": {"ARN"},
                },
                {
                    "id": "bar",
                    "org": {"LHR"},
                    "dest": {"LAX"},
                },
            ],
            2,
        ),
    ],
)
def test_trip_outbound_criteria_are_generated(
    sub_trips: Sequence[Mapping[str, Any]],
    expected: int,
) -> None:
    trips = list(
        segment_grouper.generate_trip_criteria(
            [
                segment_grouper.SubTrip(
                    trip_id=sub_trip["id"],
                    origins=frozenset(sub_trip["org"]),
                    destinations=frozenset(sub_trip["dest"]),
                    departure=datetime.datetime.now(tz=datetime.UTC),
                    arrival=datetime.datetime.now(tz=datetime.UTC),
                    segments=[],
                )
                for sub_trip in sub_trips
            ],
        ),
    )
    assert len(trips) == expected
    assert not any(criteria.inbound for criteria in trips)


def test_trip_roundtrip_criteria_are_generated(
    roundtrip: Sequence[segment_grouper.SubTrip],
) -> None:
    trips = list(segment_grouper.generate_trip_criteria(roundtrip))
    assert len(trips) == 3
    assert any(criteria.inbound for criteria in trips)


def test_trip_roundtrip_criteria_handles_reversed_order(
    roundtrip: Sequence[segment_grouper.SubTrip],
) -> None:
    sub_trips = list(roundtrip)
    trips = list(segment_grouper.generate_trip_criteria(sub_trips))
    sub_trips.reverse()
    reversed_trips = list(segment_grouper.generate_trip_criteria(sub_trips))
    assert trips == reversed_trips
