import datetime
import uuid

import freezegun
import mongomock_motor
import pytest

from snowfall.project.junction.go.service.planner.v1alpha import planner_pb2
from snowfall.project.junction.go.service.trips import trips
from snowfall.project.junction.go.service.trips.v1alpha import trips_pb2
from snowfall.project.junction.go.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf


@pytest.fixture()
def search_journey_response() -> planner_pb2.SearchJourneyResponse:
    return planner_pb2.SearchJourneyResponse(
        trips=[
            models_pb2.TripReference(
                id="trip_1",
                segments=[
                    models_pb2.SegmentReference(
                        id="segment_1",
                        leg_ids=["leg_1", "leg_2"],
                    ),
                    models_pb2.SegmentReference(
                        id="segment_2",
                        leg_ids=["leg_3", "leg_4"],
                    ),
                ],
            ),
            models_pb2.TripReference(
                id="trip_2",
                segments=[
                    models_pb2.SegmentReference(
                        id="segment_3",
                        leg_ids=["leg_5", "leg_6"],
                    ),
                    models_pb2.SegmentReference(
                        id="segment_4",
                        leg_ids=["leg_7", "leg_8"],
                    ),
                ],
            ),
        ],
    )


async def test_trip_and_segments_repository(
    search_journey_response: planner_pb2.SearchJourneyResponse,
) -> None:
    trips_repo = trips.TripRepository(
        mongomock_motor.AsyncMongoMockClient()["tests"]["test"],
        datetime.timedelta(days=1),
    )

    await trips_repo.add_multiple_if_missing(search_journey_response.trips)

    for trip_id in ("trip_1", "trip_2"):
        trip = await trips_repo.find_by_id(trip_id)

        assert trip and trip.id == trip_id

    returned_trips = await trips_repo.find(["trip_1"], cursor="")

    assert (await anext(returned_trips)).id == "trip_1"
    # TODO: test segments repository


async def _insert_trip_search(
    repository: trips.TripSearchRepository,
    trip_search: trips_pb2.TripSearch,
) -> trips_pb2.TripSearch:
    inserted = await repository.insert(trip_search)

    assert uuid.UUID(inserted.id).version == 4
    assert inserted.expires_at.ToDatetime().isoformat() == "2022-04-21T08:30:30"
    assert trip_search.departure_after == inserted.departure_after

    return inserted


@freezegun.freeze_time("2022-04-20T08:30:30Z")
async def test_trip_search_repository(
    search_journey_response: planner_pb2.SearchJourneyResponse,
) -> None:
    repo = trips.TripSearchRepository(
        mongomock_motor.AsyncMongoMockClient()["tests"]["test"],
        datetime.timedelta(days=1),
    )

    trip = trips_pb2.TripSearch(
        departure_after=protobuf.datetime_to_protobuf_datetime(
            datetime.datetime.now(datetime.timezone.utc),
        ),
    )
    inserted_trip = await _insert_trip_search(repo, trip)
    stored_trip = await repo.find_by_id(inserted_trip.id)

    assert stored_trip == inserted_trip

    updated_trip = await repo.add_results_from_journey_search(
        stored_trip,
        search_journey_response,
    )

    assert updated_trip.id == stored_trip.id
    assert len(updated_trip.trip_ids) == 2
    assert all(trip_id in updated_trip.trip_ids for trip_id in ("trip_1", "trip_2"))

    stored_trip = await repo.find_by_id(inserted_trip.id)

    assert stored_trip == updated_trip
