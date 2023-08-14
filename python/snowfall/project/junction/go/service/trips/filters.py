import datetime
from collections.abc import Sequence
from typing import NamedTuple

import more_itertools

from snowfall.project.junction.go.service.trips import orchestrator
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.stdlib.format import protobuf


class TripDuration(NamedTuple):
    trip: models_pb2.Trip
    duration: datetime.timedelta


def _trip_duration(trip: models_pb2.Trip) -> datetime.timedelta:
    return protobuf.protobuf_to_datetime(
        more_itertools.last(more_itertools.last(trip.segments).legs).arrival_at,
    ) - protobuf.protobuf_to_datetime(
        more_itertools.first(more_itertools.first(trip.segments).legs).departure_at,
    )


def _is_multimodal(trip: models_pb2.Trip) -> bool:
    return len({leg.type for segment in trip.segments for leg in segment.legs}) > 1


def _get_sorted_trip_duration_couples(
    trip_group: orchestrator.TripGroup,
) -> list[TripDuration]:
    return sorted(
        [
            TripDuration(
                trip=trip,
                duration=_trip_duration(trip),
            )
            for trip in trip_group
        ],
        key=lambda trip_duration: trip_duration.duration,
    )


def filter_trips(  # noqa: WPS210
    journey_candidates: orchestrator.JourneyCandidates,
    max_trip_length_factor: float,
) -> tuple[orchestrator.JourneyCandidates, orchestrator.JourneyCandidates]:
    filtered_groups: list[list[models_pb2.Trip]] = [
        [] for _ in range(len(journey_candidates.trip_groups))
    ]
    filtered_out_groups: list[list[models_pb2.Trip]] = [
        [] for _ in range(len(journey_candidates.trip_groups))
    ]

    for trip_seq, trip_group in enumerate(journey_candidates.trip_groups):
        sorted_trip_duration_couples = _get_sorted_trip_duration_couples(trip_group)
        lowest_dur = sorted_trip_duration_couples[0].duration

        for trip_duration_couple in sorted_trip_duration_couples:
            if trip_duration_couple.duration / lowest_dur < max_trip_length_factor:
                filtered_groups[trip_seq].append(trip_duration_couple.trip)
            else:
                filtered_out_groups[trip_seq].append(trip_duration_couple.trip)

    return orchestrator.JourneyCandidates(
        trip_groups=filtered_groups,
    ), orchestrator.JourneyCandidates(trip_groups=filtered_out_groups)


def filter_include_multimodal(
    journey_candidates: orchestrator.JourneyCandidates,
    max_trip_length_factor: float,
    max_multimodal_include: int = 2,
) -> orchestrator.JourneyCandidates:
    filtered_cands, filtered_out_cands = filter_trips(
        journey_candidates=journey_candidates,
        max_trip_length_factor=max_trip_length_factor,
    )
    trip_groups = list(filtered_cands.trip_groups)

    for trip_seq, trip_group in enumerate(filtered_cands.trip_groups):
        if any(_is_multimodal(trip) for trip in trip_group):
            continue

        trip_groups[trip_seq].extend(
            _get_n_multimodals(
                trips=filtered_out_cands.trip_groups[trip_seq],
                max_multimodal_include=max_multimodal_include,
            ),
        )

    return orchestrator.JourneyCandidates(trip_groups=trip_groups)


def _get_n_multimodals(
    trips: Sequence[models_pb2.Trip],
    max_multimodal_include: int,
) -> list[models_pb2.Trip]:
    pushed = 0
    multimodals = []

    for trip in trips:
        if _is_multimodal(trip):
            multimodals.append(trip)
            pushed += 1

            if pushed >= max_multimodal_include:
                return multimodals

    return multimodals
