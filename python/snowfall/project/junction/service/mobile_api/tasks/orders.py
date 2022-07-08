import asyncio
from typing import Any, Mapping

from snowfall.project.junction.service.mobile_api import payments, repository, resources
from snowfall.stdlib.integration.starlette import request_helpers
from snowfall.vendor.junction import client

_ORDER_STATUS_POLLING_TIMEOUT = 180
_ORDER_STATUS_POLLING_INTERVAL = 10


async def _handle_new_order_results(
    orders_repository: repository.OrdersRepository,
    order_id: str,
    payment_intent: str,
    order: Mapping[str, Any],
) -> bool:
    await orders_repository.update_order_results(order_id, order)

    order = request_helpers.flatten_request_body(order)
    order_statuses = {order_result["status"] for order_result in order["orderResults"]}
    success_statuses = {
        resources.OrderStatus.confirmed.value,
        resources.OrderStatus.not_ticketed.value,
    }
    if order_statuses and not order_statuses.difference(success_statuses):
        await payments.capture(payment_intent)
        return True

    if resources.OrderStatus.pending.value not in order_statuses:
        await payments.cancel(payment_intent)
        return True

    return False


async def poll_order_status(
    junction_client: client.JunctionClient,
    orders_repository: repository.OrdersRepository,
    order_id: str,
    payment_intent: str,
) -> bool:
    time_spent = 0
    while time_spent <= _ORDER_STATUS_POLLING_TIMEOUT:
        order = await junction_client.get_order_by_id(order_id)
        payment_processed = await _handle_new_order_results(
            orders_repository,
            order_id,
            payment_intent,
            order,
        )
        if payment_processed:
            return True

        await asyncio.sleep(_ORDER_STATUS_POLLING_INTERVAL)
        time_spent += _ORDER_STATUS_POLLING_INTERVAL

    await orders_repository.set_order_status(order_id, resources.OrderStatus.timeout)
    await payments.cancel(payment_intent)
    return False
