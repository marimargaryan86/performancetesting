import pytest

from snowfall.project.junction.plus.service.orders_registration import importer
from snowfall.project.junction.plus.service.orders_registration.v1alpha import amqp_pb2
from snowfall.stdlib.transport.amqp import types


async def test_order_fail_validation(
    order_importer: importer.OrderImporter,
    invalid_message: types.Message[amqp_pb2.IncomingOrder],
) -> None:
    with pytest.raises(ExceptionGroup, match="ProtobufValidationErrors"):
        await order_importer._process_message(invalid_message)  # noqa: SLF001
