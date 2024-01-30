import datetime
from unittest import mock

import pytest
from motor import core

from snowfall.project.junction.go.service.bridge import grpc, trip_candidates
from snowfall.project.junction.go.service.bridge.v1alpha import (
    amqp_pb2 as bridge_amqp_pb2,
)
from snowfall.project.junction.go.service.bridge.v1alpha import (
    trips_pb2 as bridge_trips_pb2,
)
from snowfall.project.junction.go.service.trips.v1alpha import trips_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport.amqp import producer
from snowfall.stdlib.transport.grpc import testing
from snowfall.stdlib.v1 import amqp_pb2


@pytest.fixture()
async def trip_candidate_search_repository(
    mongo_client: core.AgnosticClient,
) -> trip_candidates.TripCandidateSearchRepository:
    return trip_candidates.TripCandidateSearchRepository(
        mongo_client.test.trip_candidate_searches,
        datetime.timedelta(minutes=15),
    )


@pytest.fixture()
def trip_candidate_search_service_tester(
    trip_candidate_search_repository: trip_candidates.TripCandidateSearchRepository,
    producer_obj: mock.AsyncMock,
) -> testing.ServerTester:
    return testing.ServerTester(
        grpc.TripCandidateSearchService(
            producer_obj=producer_obj,
            repository=trip_candidate_search_repository,
        ),
    )


@pytest.fixture()
def producer_obj() -> mock.AsyncMock:
    return mock.create_autospec(producer.Producer, instance=True, spec_set=True)


async def test_search_task_published(
    trip_candidate_search_service_tester: testing.ServerTester,
    producer_obj: mock.AsyncMock,
) -> None:
    response = await trip_candidate_search_service_tester.invoke_unary_unary(
        method=grpc.TripCandidateSearchService.EnqueueTripCandidateSearch,
        request=bridge_trips_pb2.EnqueueTripCandidateSearchRequest(
            trip_candidate_search=trips_pb2.TripCandidateSearch(),
        ),
    )

    producer_obj.publish.assert_called_once_with(
        bridge_amqp_pb2.TripCandidateSearchTask(
            trip_candidate_search=response.message.trip_candidate_search,
        ),
        "bridge.trip_candidates.search",
    )


async def test_search_task_persisted(
    trip_candidate_search_service_tester: testing.ServerTester,
    trip_candidate_search_repository: trip_candidates.TripCandidateSearchRepository,
) -> None:
    response = await trip_candidate_search_service_tester.invoke_unary_unary(
        method=grpc.TripCandidateSearchService.EnqueueTripCandidateSearch,
        request=bridge_trips_pb2.EnqueueTripCandidateSearchRequest(
            trip_candidate_search=trips_pb2.TripCandidateSearch(),
        ),
    )

    persisted = await trip_candidate_search_repository.find_by_id(
        response.message.trip_candidate_search.id,
    )

    assert persisted is not None

    assert persisted.id == response.message.trip_candidate_search.id


async def test_search_task_created_correctly(
    trip_candidate_search_service_tester: testing.ServerTester,
) -> None:
    response = await trip_candidate_search_service_tester.invoke_unary_unary(
        method=grpc.TripCandidateSearchService.EnqueueTripCandidateSearch,
        request=bridge_trips_pb2.EnqueueTripCandidateSearchRequest(
            trip_candidate_search=trips_pb2.TripCandidateSearch(),
        ),
    )

    now = datetime.datetime.now(tz=datetime.UTC)

    assert response.message.trip_candidate_search.id != ""
    assert (
        response.message.trip_candidate_search.status
        == amqp_pb2.Trackable.STATUS_PENDING
    )
    assert (
        protobuf.protobuf_to_datetime(response.message.trip_candidate_search.expires_at)
        > now
    )
