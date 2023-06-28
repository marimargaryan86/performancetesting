from unittest.mock import call

from snowfall.project.junction.plus.service.orders_registration import importer
from snowfall.project.junction.plus.service.orders_registration.v1alpha import amqp_pb2
from snowfall.stdlib.transport.amqp import types


async def test_order_fail_validation(
    order_importer: importer.OrderImporter,
    invalid_message: types.Message[amqp_pb2.IncomingOrder],
) -> None:
    await order_importer._process_message(invalid_message)  # noqa: WPS437
    assert order_importer._logger.warning.call_args_list[0] == call(  # type: ignore[attr-defined] # noqa: WPS437
        "Validation Error",
        exc_info=True,
    )
