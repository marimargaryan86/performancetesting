import asyncio
import datetime
from typing import Any
from unittest import mock

import grpc
import more_itertools
import pymongo
import pytest

from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.go.service.orders import orders
from snowfall.project.junction.go.service.orders.v1 import models_pb2, orders_pb2
from snowfall.project.junction.go.service.resellers.v1 import (
    models_pb2 as reseller_models_pb2,
)
from snowfall.project.junction.go.service.resellers.v1 import resellers_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf

_RESELLER_ID = "foo"
_JOURNEY_PARENTS = ("bar", "baz")


@pytest.fixture()
async def journey_with_owners(
    resellers_client: Any,
    journey_repository: orders.JourneyRepository,
) -> models_pb2.Journey:
    resellers_client.GetReseller = mock.AsyncMock(
        return_value=resellers_pb2.GetResellerResponse(
            reseller=reseller_models_pb2.Reseller(
                parent_reseller_ids=_JOURNEY_PARENTS,
            ),
        ),
    )
    return await journey_repository.create(
        contact_details=models_pb2.ContactDetails(),
        reseller_id=_RESELLER_ID,
    )


async def create_journeys_with_orders(
    number_of_journeys: int,
    journey_repository: orders.JourneyRepository,
    order_repository: orders.OrderRepository,
) -> None:
    for idx in range(number_of_journeys):
        journey = await journey_repository.create(
            contact_details=models_pb2.ContactDetails(),
            reseller_id="",
        )

        await order_repository.create_from_options(
            journey_id=journey.id,
            passengers=[
                models_pb2.Passenger(),
            ],
            options=[
                models_pb2.TripOption(
                    details=[
                        models_pb2.TripOptionDetails(
                            segment=offers_pb2.OfferSegment(
                                legs=[
                                    offers_pb2.OfferSegmentLeg(
                                        id=string.uuid(),
                                        departure_at=protobuf.datetime_to_protobuf(
                                            datetime.datetime.now(
                                                tz=datetime.UTC,
                                            )
                                            + datetime.timedelta(days=idx),
                                        ),
                                        arrival_at=protobuf.datetime_to_protobuf(
                                            datetime.datetime.now(
                                                tz=datetime.UTC,
                                            )
                                            + datetime.timedelta(days=idx + 1),
                                        ),
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            ],
            residence_address=None,
        )


class TestJourneys(object):
    async def test_created_journey_has_owners_with_not_found_reseller(
        self,
        resellers_client: Any,
        journey_repository: orders.JourneyRepository,
    ) -> None:
        error = grpc.aio.AioRpcError(
            code=grpc.StatusCode.NOT_FOUND,
            initial_metadata=grpc.aio.Metadata(),
            trailing_metadata=grpc.aio.Metadata(),
        )
        resellers_client.GetReseller = mock.AsyncMock(side_effect=error)
        journey = await journey_repository.create(
            contact_details=models_pb2.ContactDetails(),
            reseller_id=_RESELLER_ID,
        )
        assert len(journey.owner_reseller_ids) == 1
        assert _RESELLER_ID in journey.owner_reseller_ids

    async def test_created_journey_has_owners_with_reseller_without_parents(
        self,
        resellers_client: Any,
        journey_repository: orders.JourneyRepository,
    ) -> None:
        journey = await journey_repository.create(
            contact_details=models_pb2.ContactDetails(),
            reseller_id=_RESELLER_ID,
        )
        assert len(journey.owner_reseller_ids) == 1
        assert _RESELLER_ID in journey.owner_reseller_ids

    async def test_created_journey_has_reseller_parents_owners(
        self,
        journey_with_owners: models_pb2.Journey,
    ) -> None:
        assert len(journey_with_owners.owner_reseller_ids) == 3
        assert _RESELLER_ID in journey_with_owners.owner_reseller_ids

        for parent in _JOURNEY_PARENTS:
            assert parent in journey_with_owners.owner_reseller_ids

    @pytest.mark.parametrize(
        "reseller_id",
        [
            _RESELLER_ID,
            *_JOURNEY_PARENTS,
        ],
    )
    async def test_journey_is_retrievable_by_owners(
        self,
        journey_repository: orders.JourneyRepository,
        journey_with_owners: models_pb2.Journey,
        reseller_id: str,
    ) -> None:
        journey = await journey_repository.find_by_id(
            journey_with_owners.id,
            reseller_id,
        )
        assert journey
        assert journey.id == journey_with_owners.id

    async def test_journey_is_not_retrievable_by_unknown_reseller(
        self,
        journey_repository: orders.JourneyRepository,
        journey_with_owners: models_pb2.Journey,
    ) -> None:
        journey = await journey_repository.find_by_id(
            journey_with_owners.id,
            "qux",
        )
        assert not journey

    async def test_journey_is_retrievable_by_id(
        self,
        journey_repository: orders.JourneyRepository,
        order: models_pb2.Order,
    ) -> None:
        journey = await journey_repository.find_by_id(order.journey_id)
        assert journey
        assert journey.id == order.journey_id

    async def test_journey_is_retrievable_by_ids(
        self,
        journey_repository: orders.JourneyRepository,
        order: models_pb2.Order,
    ) -> None:
        journeys_result = await journey_repository.find([order.journey_id], "")
        journeys = [journey async for journey in journeys_result]

        assert len(journeys) == 1
        assert more_itertools.first(journeys).id == order.journey_id

    async def test_sorting_by_id(
        self,
        journey_repository: orders.JourneyRepository,
    ) -> None:
        await asyncio.gather(
            journey_repository.create(
                contact_details=models_pb2.ContactDetails(),
                reseller_id="",
            ),
            journey_repository.create(
                contact_details=models_pb2.ContactDetails(),
                reseller_id="",
            ),
        )

        asc_id_journeys = [
            journey.id
            async for journey in await journey_repository.find(
                ids=[],
                cursor="",
                sort=("_id", pymongo.ASCENDING),
            )
        ]

        desc_id_journeys = [
            journey.id
            async for journey in await journey_repository.find(
                ids=[],
                cursor="",
                sort=("_id", pymongo.DESCENDING),
            )
        ]

        assert len(asc_id_journeys) == 2
        assert asc_id_journeys[0] == desc_id_journeys[1]
        assert asc_id_journeys[1] == desc_id_journeys[0]

    async def test_sorting_by_pnr(
        self,
        journey_repository: orders.JourneyRepository,
    ) -> None:
        await asyncio.gather(
            journey_repository.create(
                contact_details=models_pb2.ContactDetails(),
                reseller_id="",
            ),
            journey_repository.create(
                contact_details=models_pb2.ContactDetails(),
                reseller_id="",
            ),
        )

        asc_pnr_journeys = [
            journey.passenger_name_record
            async for journey in await journey_repository.find(
                ids=[],
                cursor="",
                sort=("passenger_name_record", pymongo.ASCENDING),
            )
        ]

        desc_pnr_journeys = [
            journey.passenger_name_record
            async for journey in await journey_repository.find(
                ids=[],
                cursor="",
                sort=("passenger_name_record", pymongo.DESCENDING),
            )
        ]

        assert len(asc_pnr_journeys) == 2
        assert asc_pnr_journeys[0] == desc_pnr_journeys[1]
        assert asc_pnr_journeys[1] == desc_pnr_journeys[0]

    async def test_sorting_by_created_at(
        self,
        journey_repository: orders.JourneyRepository,
    ) -> None:
        await asyncio.gather(
            journey_repository.create(
                contact_details=models_pb2.ContactDetails(),
                reseller_id="",
            ),
            journey_repository.create(
                contact_details=models_pb2.ContactDetails(),
                reseller_id="",
            ),
        )

        asc_created_at_journeys = [
            journey.created_at
            async for journey in await journey_repository.find(
                ids=[],
                cursor="",
                sort=("created_at", pymongo.ASCENDING),
            )
        ]

        desc_created_at_journeys = [
            journey.created_at
            async for journey in await journey_repository.find(
                ids=[],
                cursor="",
                sort=("created_at", pymongo.DESCENDING),
            )
        ]

        assert len(asc_created_at_journeys) == 2
        assert asc_created_at_journeys[0] == desc_created_at_journeys[1]
        assert asc_created_at_journeys[1] == desc_created_at_journeys[0]

    async def test_filter_by_departure_at(
        self,
        journey_repository: orders.JourneyRepository,
        order_repository: orders.OrderRepository,
    ) -> None:
        await create_journeys_with_orders(3, journey_repository, order_repository)

        all_journeys = [
            journey
            async for journey in await journey_repository.find(ids=[], cursor="")
        ]
        assert len(all_journeys) == 3

        filtered_journeys = [
            journey
            async for journey in await journey_repository.find(
                ids=[],
                cursor="",
                filter_by=[
                    orders_pb2.ListJourneysRequest.JourneyFilter(
                        operator="ge",
                        departure_at=protobuf.datetime_to_protobuf(
                            datetime.datetime.now(tz=datetime.UTC)
                            - datetime.timedelta(days=1),
                        ),
                    ),
                    orders_pb2.ListJourneysRequest.JourneyFilter(
                        operator="le",
                        departure_at=protobuf.datetime_to_protobuf(
                            datetime.datetime.now(tz=datetime.UTC)
                            + datetime.timedelta(days=1),
                        ),
                    ),
                ],
            )
        ]
        assert len(filtered_journeys) == 2

    async def test_filter_by_created_at(
        self,
        journey_repository: orders.JourneyRepository,
        order_repository: orders.OrderRepository,
    ) -> None:
        await create_journeys_with_orders(3, journey_repository, order_repository)

        all_journeys = [
            journey
            async for journey in await journey_repository.find(ids=[], cursor="")
        ]
        assert len(all_journeys) == 3

        filtered_journeys = [
            journey
            async for journey in await journey_repository.find(
                ids=[],
                cursor="",
                filter_by=[
                    orders_pb2.ListJourneysRequest.JourneyFilter(
                        operator="le",
                        order_created_at=protobuf.datetime_to_protobuf(
                            datetime.datetime.now(tz=datetime.UTC)
                            - datetime.timedelta(days=1),
                        ),
                    ),
                ],
            )
        ]
        assert not filtered_journeys

    async def test_filter_by_booking_status(
        self,
        journey_repository: orders.JourneyRepository,
        order_repository: orders.OrderRepository,
    ) -> None:
        await create_journeys_with_orders(3, journey_repository, order_repository)

        all_journeys = [
            journey
            async for journey in await journey_repository.find(ids=[], cursor="")
        ]
        assert len(all_journeys) == 3

        filtered_journeys = [
            journey
            async for journey in await journey_repository.find(
                ids=[],
                cursor="",
                filter_by=[
                    orders_pb2.ListJourneysRequest.JourneyFilter(
                        operator="eq",
                        booking_status=models_pb2.Booking.Status.STATUS_PENDING,
                    ),
                ],
            )
        ]
        assert len(filtered_journeys) == 3

        filtered_journeys = [
            journey
            async for journey in await journey_repository.find(
                ids=[],
                cursor="",
                filter_by=[
                    orders_pb2.ListJourneysRequest.JourneyFilter(
                        operator="eq",
                        booking_status=models_pb2.Booking.Status.STATUS_CONFIRMED,
                    ),
                ],
            )
        ]
        assert not filtered_journeys


class TestOrders(object):
    async def test_order_is_retrievable_by_id(
        self,
        order_repository: orders.OrderRepository,
        order: models_pb2.Order,
    ) -> None:
        order_resource = await order_repository.find_by_id(order.id)
        assert order_resource
        assert order_resource.id == order.id


class TestBookings(object):
    async def test_booking_can_be_retrieved(
        self,
        booking_repository: orders.BookingRepository,
        order: models_pb2.Order,
    ) -> None:
        booking_id = more_itertools.first(order.bookings).id
        booking = await booking_repository.find_by_id(booking_id)
        assert booking
        assert booking_id == booking.id


class TestBookingDetails(object):
    async def test_booking_details_can_be_retrieved(
        self,
        booking_repository: orders.BookingRepository,
        booking_details_repository: orders.BookingDetailsRepository,
        order: models_pb2.Order,
    ) -> None:
        booking_id = more_itertools.first(order.bookings).id
        booking = await booking_repository.find_by_id(booking_id)
        assert booking
        detail_id = more_itertools.first(booking.trip_option.details).id
        detail = await booking_details_repository.find_by_id(detail_id)
        assert detail
        assert detail_id == detail.id
        assert booking_id == detail.booking_id

    async def test_booking_details_can_be_retrieved_by_ids(
        self,
        booking_repository: orders.BookingRepository,
        booking_details_repository: orders.BookingDetailsRepository,
        order: models_pb2.Order,
    ) -> None:
        booking_id = more_itertools.first(order.bookings).id
        booking = await booking_repository.find_by_id(booking_id)
        assert booking
        detail_ids = [detail.id for detail in booking.trip_option.details]
        details = await booking_details_repository.find(detail_ids, "")
        assert len([detail async for detail in details]) == 2

    async def test_booking_details_can_be_retrieved_by_booking(
        self,
        booking_repository: orders.BookingRepository,
        booking_details_repository: orders.BookingDetailsRepository,
        order: models_pb2.Order,
    ) -> None:
        booking_id = more_itertools.first(order.bookings).id
        details = await booking_details_repository.find_by_booking_id(booking_id, "")
        assert len([detail async for detail in details]) == 2


class TestCancellationRequests(object):
    async def test_cancellation_request_is_retrievable_by_id(
        self,
        cancellation_requests_repository: orders.CancellationRequestsRepository,
        cancellation_request: models_pb2.CancellationRequest,
    ) -> None:
        retrieved = await cancellation_requests_repository.find_by_id(
            cancellation_request.id,
        )
        assert retrieved
        assert retrieved.id == cancellation_request.id
        assert retrieved.status == cancellation_request.status
        assert retrieved.created_at.seconds == cancellation_request.created_at.seconds

    async def test_cancellation_request_is_retrievable_by_booking_id(
        self,
        cancellation_requests_repository: orders.CancellationRequestsRepository,
        cancellation_request: models_pb2.CancellationRequest,
    ) -> None:
        booking_id = more_itertools.first(
            cancellation_request.booking_cancellations,
        ).booking_id

        retrieved = await cancellation_requests_repository.find_by_booking_id(
            booking_id,
        )

        assert retrieved
        assert retrieved.id == cancellation_request.id
        assert retrieved.status == cancellation_request.status
        for retrieved_bc, expected_bc in list(  # noqa: WPS352
            zip(
                retrieved.booking_cancellations,
                cancellation_request.booking_cancellations,
                strict=True,
            ),
        ):
            assert retrieved_bc == expected_bc

    async def test_cancellation_request_is_retrievable_by_ticket_id(
        self,
        cancellation_requests_repository: orders.CancellationRequestsRepository,
        cancellation_request: models_pb2.CancellationRequest,
    ) -> None:
        ticket_id = more_itertools.first(
            cancellation_request.booking_cancellations,
        ).ticket_id

        retrieved = await cancellation_requests_repository.find_by_ticket_id(ticket_id)

        assert retrieved
        assert retrieved.id == cancellation_request.id
        assert retrieved.status == cancellation_request.status
        for retrieved_bc, expected_bc in list(  # noqa: WPS352
            zip(
                retrieved.booking_cancellations,
                cancellation_request.booking_cancellations,
                strict=True,
            ),
        ):
            assert retrieved_bc == expected_bc

    async def test_cancellation_request_is_retrievable_by_booking_cancellation_id(
        self,
        cancellation_requests_repository: orders.CancellationRequestsRepository,
        cancellation_request: models_pb2.CancellationRequest,
    ) -> None:
        booking_cancellation_id = more_itertools.first(
            cancellation_request.booking_cancellations,
        ).id

        retrieved = (
            await cancellation_requests_repository.find_by_booking_cancellation_id(
                booking_cancellation_id,
            )
        )

        assert retrieved
        assert retrieved.id == cancellation_request.id
        assert retrieved.status == cancellation_request.status
        for retrieved_bc, expected_bc in list(  # noqa: WPS352
            zip(
                retrieved.booking_cancellations,
                cancellation_request.booking_cancellations,
                strict=True,
            ),
        ):
            assert retrieved_bc == expected_bc

    async def test_can_update_cancellation_status(
        self,
        cancellation_requests_repository: orders.CancellationRequestsRepository,
        cancellation_request: models_pb2.CancellationRequest,
    ) -> None:
        cancellation_request.status = models_pb2.CancellationRequest.STATUS_COMPLETED

        update_success = await cancellation_requests_repository.update(
            cancellation_request,
        )

        updated = await cancellation_requests_repository.find_by_id(
            cancellation_request.id,
        )

        assert update_success
        assert updated
        assert updated.id == cancellation_request.id
        assert updated.status == cancellation_request.status


class TestBookingCancellations(object):
    async def test_booking_cancellation_is_retrievable_by_id(
        self,
        booking_cancellations_repository: orders.BookingCancellationsRepository,
        cancellation_request: models_pb2.CancellationRequest,
    ) -> None:
        booking_cancellation = more_itertools.first(
            cancellation_request.booking_cancellations,
        )
        retrieved = await booking_cancellations_repository.find_by_id(
            booking_cancellation.id,
            cancellation_request.reseller_id,
        )

        assert retrieved
        assert retrieved.id == booking_cancellation.id
        assert retrieved.status == booking_cancellation.status

    async def test_booking_cancellation_is_retrievable_by_booking_id(
        self,
        booking_cancellations_repository: orders.BookingCancellationsRepository,
        cancellation_request: models_pb2.CancellationRequest,
    ) -> None:
        booking_cancellation = more_itertools.first(
            cancellation_request.booking_cancellations,
        )

        retrieved = await booking_cancellations_repository.find_by_booking_id(
            booking_cancellation.booking_id,
            cancellation_request.reseller_id,
        )

        assert retrieved
        assert retrieved.id == booking_cancellation.id
        assert retrieved.status == booking_cancellation.status

    async def test_find_booking_cancellation_by_id_not_found(
        self,
        booking_cancellations_repository: orders.BookingCancellationsRepository,
    ) -> None:
        retrieved = await booking_cancellations_repository.find_by_id(
            document_id="",
            reseller_id="",
        )

        assert not retrieved

    async def test_find_booking_cancellation_by_booking_id_not_found(
        self,
        booking_cancellations_repository: orders.BookingCancellationsRepository,
    ) -> None:
        retrieved = await booking_cancellations_repository.find_by_booking_id(
            document_id="",
            reseller_id="",
        )

        assert not retrieved

    async def test_find_booking_cancellations_by_ids(
        self,
        booking_cancellations_repository: orders.BookingCancellationsRepository,
        cancellation_request: models_pb2.CancellationRequest,
    ) -> None:
        ids = [
            booking_cancellation.id
            for booking_cancellation in cancellation_request.booking_cancellations
        ]

        retrieved = await booking_cancellations_repository.find(
            ids=ids,
            reseller_id=cancellation_request.reseller_id,
        )

        result_count = 0
        async for booking_cancellation in retrieved:
            result_count += 1
            assert booking_cancellation.id in ids

        assert result_count == len(ids)

    async def test_find_booking_cancellations_by_booking_ids(
        self,
        booking_cancellations_repository: orders.BookingCancellationsRepository,
        cancellation_request: models_pb2.CancellationRequest,
    ) -> None:
        booking_ids = [
            booking_cancellation.booking_id
            for booking_cancellation in cancellation_request.booking_cancellations
        ]

        retrieved = await booking_cancellations_repository.find_by_booking_ids(
            booking_ids=booking_ids,
            reseller_id=cancellation_request.reseller_id,
        )

        result_count = 0
        async for booking_cancellation in retrieved:
            result_count += 1
            assert booking_cancellation.booking_id in booking_ids

        assert result_count == len(booking_ids)
