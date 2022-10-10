import asyncio
import datetime
from typing import Any, Mapping, Sequence

import aiofiles
from jinja2 import Template

from snowfall.project.junction.service.mobile_api import (
    payments,
    repository,
    resources,
    smtp,
)
from snowfall.stdlib.integration.starlette import request_helpers
from snowfall.stdlib.persistence import filesystem
from snowfall.vendor.junction import client

_ORDER_STATUS_POLLING_TIMEOUT = 180
_ORDER_STATUS_POLLING_INTERVAL = 10
_ATTRIBUTES_ACCESSOR = "attributes"


async def _handle_new_order_results(
    orders_repository: repository.OrdersRepository,
    order_id: str,
    payment_intent: str,
    order: Mapping[str, Any],
    smtp_client: smtp.EmailClient,
) -> bool:
    await orders_repository.update_order_results(order_id, order)
    mobile_order = (
        await orders_repository.find_by_id(
            order["data"]["id"],
            "attributes.junctionOrderId",
        )
        or {}
    )
    order = request_helpers.flatten_request_body(order)
    order_statuses = {order_result["status"] for order_result in order["orderResults"]}
    success_statuses = {
        resources.OrderStatus.confirmed.value,
        resources.OrderStatus.not_ticketed.value,
    }
    if order_statuses and not order_statuses.difference(success_statuses):
        await payments.capture(payment_intent)
        await send_booking_confirmation(mobile_order, smtp_client)
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
    smtp_client: smtp.EmailClient,
) -> bool:
    time_spent = 0
    while time_spent <= _ORDER_STATUS_POLLING_TIMEOUT:
        order = await junction_client.get_order_by_id(order_id)
        payment_processed = await _handle_new_order_results(
            orders_repository,
            order_id,
            payment_intent,
            order,
            smtp_client,
        )
        if payment_processed:
            return True

        await asyncio.sleep(_ORDER_STATUS_POLLING_INTERVAL)
        time_spent += _ORDER_STATUS_POLLING_INTERVAL

    await orders_repository.set_order_status(order_id, resources.OrderStatus.timeout)
    await payments.cancel(payment_intent)
    return False


async def send_booking_confirmation(
    order: Mapping[str, Any],
    smtp_client: smtp.EmailClient,
) -> None:
    details = get_group_details_from_order(order)
    details = order_details_by_date(details)
    async with aiofiles.open(
        filesystem.resource_path(
            "snowfall.project.junction.service.mobile_api.html_templates",
            "booking_template.html",
        ),
    ) as template_file:
        template = Template(await template_file.read())
    body = template.render(
        details=details,
        reference=order[_ATTRIBUTES_ACCESSOR]["reference"],
        company_name=smtp_client.client_name,
    )
    await smtp_client.send_email_html_template(
        order[_ATTRIBUTES_ACCESSOR]["contactDetails"]["email"],
        "Journey details for Booking {reference}".format(
            reference=order[_ATTRIBUTES_ACCESSOR]["reference"],
        ),
        body,
    )
    await smtp_client.send_email_html_template(
        smtp_client.support_email,
        "Journey details for Booking {reference}".format(
            reference=order[_ATTRIBUTES_ACCESSOR]["reference"],
        ),
        body,
    )


def get_group_details_from_order(
    order: Mapping[str, Any],
) -> Sequence[Mapping[str, Any]]:
    groups = order[_ATTRIBUTES_ACCESSOR]["offer"][_ATTRIBUTES_ACCESSOR]["groups"]
    return [
        detail[_ATTRIBUTES_ACCESSOR]
        for group in groups
        for detail in group[_ATTRIBUTES_ACCESSOR]["details"]
    ]


def order_details_by_date(
    details: Sequence[Mapping[str, Any]],
) -> Sequence[Mapping[str, Any]]:
    ordered_details = [
        {
            "origin": leg["origin"],
            "destination": leg["destination"],
            "departureAt": datetime.datetime.fromisoformat(leg["departureAt"]).strftime(
                "%A %d %b %Y %H:%M",
            ),
            "arrivalAt": datetime.datetime.fromisoformat(leg["arrivalAt"]).strftime(
                "%A %d %b %Y %H:%M",
            ),
            "ref": segment["vendor"] + segment["routeIdentifiers"]["vendor"],
            "legType": segment["legType"],
        }
        for segment in details
        for leg in segment["legs"]
    ]
    ordered_details.sort(key=lambda leg: leg["departureAt"])
    return ordered_details
