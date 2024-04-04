from __future__ import annotations

from unittest import mock

import grpc
import pytest
from motor import motor_asyncio

from snowfall.project.junction.rocket.service.bookings import (
    amqp,
    bookings,
    repository,
)
from snowfall.project.junction.rocket.service.bookings import grpc as bookings_grpc
from snowfall.project.junction.rocket.service.bookings.v1alpha import (
    amqp_pb2,
    grpc_pb2,
    models_pb2,
)
from snowfall.project.junction.rocket.service.gateway.v1alpha import (
    bookings_pb2_grpc,
    meta_pb2_grpc,
)
from snowfall.stdlib.transport.amqp import producer
from snowfall.stdlib.transport.grpc import testing

_booking = models_pb2.Booking(
    reseller_id="reseller-id",
)


def _abort_context(
    code: grpc.StatusCode,
    details: str | None = None,
    trailing_metadata: tuple[tuple[str, str], ...] | None = None,
) -> None:
    raise testing.AbortError(
        code=code,
        details=details,
        trailing_metadata=trailing_metadata,
    )


@pytest.fixture()
def grpc_context() -> grpc.aio.ServicerContext:
    context = mock.create_autospec(grpc.aio.ServicerContext)
    context.abort = mock.Mock(side_effect=_abort_context)

    return context


@pytest.fixture()
async def booking_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> repository.BookingRepository:
    return repository.BookingRepository(
        collection=mongo_client.test.bookings,
    )


@pytest.fixture()
async def booking_cancellation_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> repository.BookingCancellationRepository:
    return repository.BookingCancellationRepository(
        collection=mongo_client.test.cancellations,
    )


@pytest.fixture()
def booking_producer_obj() -> mock.AsyncMock:
    return mock.create_autospec(producer.Producer, instance=True, spec_set=True)


@pytest.fixture()
def cancellation_producer_obj() -> mock.AsyncMock:
    return mock.create_autospec(producer.Producer, instance=True, spec_set=True)


@pytest.fixture()
def booking_service_tester(
    booking_repository: repository.BookingRepository,
    booking_cancellation_repository: repository.BookingCancellationRepository,
    booking_producer_obj: mock.AsyncMock,
    cancellation_producer_obj: mock.AsyncMock,
) -> testing.ServerTester:
    cancellations = bookings_grpc.Cancellations(
        repository=booking_cancellation_repository,
        task_producer=amqp.BookingCancellationTaskProducer(
            producer_obj=cancellation_producer_obj,
        ),
    )
    gateway_meta_stub = mock.create_autospec(meta_pb2_grpc.MetaServiceStub)
    gateway_booking_stub = mock.create_autospec(bookings_pb2_grpc.BookingServiceStub)
    booking_handler = bookings.BookingHandler(
        gateway=gateway_booking_stub,
        fallback_bookings=booking_repository,
    )

    return testing.ServerTester(
        bookings_grpc.BookingService(
            booking_handler=booking_handler,
            booking_repository=booking_repository,
            publisher=amqp.BookingProducer(
                producer_obj=booking_producer_obj,
            ),
            default_page_size=100,
            environment="test",
            gateway_meta=gateway_meta_stub,
            cancellations=cancellations,
        ),
    )


@pytest.fixture()
def booking_service(
    booking_repository: repository.BookingRepository,
    booking_cancellation_repository: repository.BookingCancellationRepository,
    booking_producer_obj: mock.AsyncMock,
    cancellation_producer_obj: mock.AsyncMock,
) -> bookings_grpc.BookingService:
    cancellations = bookings_grpc.Cancellations(
        repository=booking_cancellation_repository,
        task_producer=amqp.BookingCancellationTaskProducer(
            producer_obj=cancellation_producer_obj,
        ),
    )
    gateway_meta_stub = mock.create_autospec(meta_pb2_grpc.MetaServiceStub)
    gateway_booking_stub = mock.create_autospec(bookings_pb2_grpc.BookingServiceStub)
    booking_handler = bookings.BookingHandler(
        gateway=gateway_booking_stub,
        fallback_bookings=booking_repository,
    )

    return bookings_grpc.BookingService(
        booking_handler=booking_handler,
        booking_repository=booking_repository,
        publisher=amqp.BookingProducer(
            producer_obj=booking_producer_obj,
        ),
        default_page_size=100,
        environment="test",
        gateway_meta=gateway_meta_stub,
        cancellations=cancellations,
    )


async def test_booking_cancellation_published(
    booking_repository: repository.BookingRepository,
    booking_service_tester: testing.ServerTester,
    cancellation_producer_obj: mock.AsyncMock,
    booking_service: bookings_grpc.BookingService,
    grpc_context: grpc.aio.ServicerContext,
) -> None:
    booking = await booking_repository.insert(_booking)

    cancellation = models_pb2.BookingCancellation(
        booking_id=booking.id,
    )

    response = await booking_service.CreateBookingCancellation(
        request=grpc_pb2.CreateBookingCancellationRequest(
            booking_cancellation=cancellation,
            reseller_id="reseller-id",
        ),
        context=grpc_context,
    )

    cancellation_producer_obj.publish.assert_called_once_with(
        amqp_pb2.HandleBookingCancellationTask(
            booking_cancellation=response.booking_cancellation,
        ),
        "bookings.cancellations",
    )


async def test_booking_cancellation_persisted(
    booking_service_tester: testing.ServerTester,
    booking_repository: repository.BookingRepository,
    booking_cancellation_repository: repository.BookingCancellationRepository,
    booking_service: bookings_grpc.BookingService,
    grpc_context: grpc.aio.ServicerContext,
) -> None:
    booking = await booking_repository.insert(_booking)

    cancellation = models_pb2.BookingCancellation(
        booking_id=booking.id,
        status=models_pb2.BookingCancellation.STATUS_PENDING,
    )

    response = await booking_service.CreateBookingCancellation(
        request=grpc_pb2.CreateBookingCancellationRequest(
            booking_cancellation=cancellation,
            reseller_id="reseller-id",
        ),
        context=grpc_context,
    )

    persisted = await booking_cancellation_repository.find_by_id(
        response.booking_cancellation.id,
    )

    assert persisted is not None


async def test_booking_cancellation_fails_for_wrong_reseller(
    booking_service_tester: testing.ServerTester,
    booking_repository: repository.BookingRepository,
    booking_service: bookings_grpc.BookingService,
    grpc_context: grpc.aio.ServicerContext,
) -> None:
    booking = await booking_repository.insert(_booking)

    cancellation = models_pb2.BookingCancellation(
        booking_id=booking.id,
    )

    with testing.assert_aborted(grpc.StatusCode.PERMISSION_DENIED):
        await booking_service.CreateBookingCancellation(
            request=grpc_pb2.CreateBookingCancellationRequest(
                booking_cancellation=cancellation,
                reseller_id="wrong-reseller-id",
            ),
            context=grpc_context,
        )


async def test_booking_cancellation_fails_for_wrong_booking_id(
    booking_service_tester: testing.ServerTester,
    booking_repository: repository.BookingRepository,
    booking_service: bookings_grpc.BookingService,
    grpc_context: grpc.aio.ServicerContext,
) -> None:
    await booking_repository.insert(_booking)

    cancellation = models_pb2.BookingCancellation(
        booking_id="wrong-booking-id",
    )

    with testing.assert_aborted(grpc.StatusCode.NOT_FOUND):
        await booking_service.CreateBookingCancellation(
            request=grpc_pb2.CreateBookingCancellationRequest(
                booking_cancellation=cancellation,
                reseller_id="reseller-id",
            ),
            context=grpc_context,
        )
