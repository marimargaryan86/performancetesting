import asyncio

from snowfall.junction.mobile_api import payments, repository
from snowfall.stdlib.integration.starlette import request_helpers
from snowfall.vendor.junction import client

_ORDER_STATUS_POLLING_TIMEOUT = 25
_ORDER_STATUS_POLLING_INTERVAL = 4


async def poll_order_status(
    junction_client: client.JunctionClient,
    orders_repository: repository.OrdersRepository,
    order_id: str,
    payment_intent: str,
) -> bool:
    time_spent = 0
    while time_spent <= _ORDER_STATUS_POLLING_TIMEOUT:
        order = await junction_client.get_order_by_id(order_id)
        await orders_repository.update_order_results(order_id, order)

        order = request_helpers.flatten_request_body(order)
        orders_confirmed_generator = (
            order_result["status"] == "confirmed"
            for order_result in order["orderResults"]
        )
        if all(orders_confirmed_generator):
            payments.capture(payment_intent)
            return True

        await asyncio.sleep(_ORDER_STATUS_POLLING_INTERVAL)
        time_spent += _ORDER_STATUS_POLLING_INTERVAL

    payments.cancel(payment_intent)
    return False
