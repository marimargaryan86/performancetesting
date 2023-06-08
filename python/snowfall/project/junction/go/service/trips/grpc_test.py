from collections.abc import Sequence

import pytest

from snowfall.project.junction.go.service.trips import grpc
from snowfall.stdlib.v1 import amqp_pb2


@pytest.mark.parametrize(
    ("statuses", "expected"),
    [
        (
            [
                amqp_pb2.Trackable.Status.STATUS_COMPLETED,
                amqp_pb2.Trackable.Status.STATUS_FAILED,
            ],
            amqp_pb2.Trackable.Status.STATUS_COMPLETED,
        ),
        (
            [
                amqp_pb2.Trackable.Status.STATUS_FAILED,
            ],
            amqp_pb2.Trackable.Status.STATUS_FAILED,
        ),
        (
            [
                amqp_pb2.Trackable.Status.STATUS_COMPLETED,
            ],
            amqp_pb2.Trackable.Status.STATUS_COMPLETED,
        ),
        (
            [
                amqp_pb2.Trackable.Status.STATUS_PROCESSING,
                amqp_pb2.Trackable.Status.STATUS_COMPLETED,
                amqp_pb2.Trackable.Status.STATUS_FAILED,
            ],
            amqp_pb2.Trackable.Status.STATUS_PROCESSING,
        ),
        (
            [],
            amqp_pb2.Trackable.Status.STATUS_PENDING,
        ),
        (
            [
                amqp_pb2.Trackable.Status.STATUS_PROCESSING,
                amqp_pb2.Trackable.Status.STATUS_PENDING,
            ],
            amqp_pb2.Trackable.Status.STATUS_PROCESSING,
        ),
    ],
)
def test_status_from_statuses(
    statuses: Sequence[amqp_pb2.Trackable.Status.ValueType],
    expected: amqp_pb2.Trackable.Status.ValueType,
) -> None:
    assert grpc.status_from_statuses(statuses) == expected
