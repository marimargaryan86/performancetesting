import asyncio
import datetime
from typing import Any, Mapping, Sequence

import aiofiles
from jinja2 import Template

from snowfall.project.junction.service.mobile_api import payments, resources, smtp
from snowfall.stdlib.persistence import filesystem
from snowfall.vendor.junction import client

_ORDER_STATUS_POLLING_TIMEOUT = 180
_ORDER_STATUS_POLLING_INTERVAL = 10
_ATTRIBUTES_ACCESSOR = "attributes"


async def _handle_new_order_results(
    payment_intent_id: str,
    order: Mapping[str, Any],
    smtp_client: smtp.EmailClient,
) -> bool:
    booking_statuses = {
        booking["relationships"]["status"]["data"]["id"]
        for booking in order["included"]
    }
    success_statuses = {
        resources.OrderStatus.confirmed.value,
        resources.OrderStatus.not_ticketed.value,
    }
    if booking_statuses and not booking_statuses.difference(success_statuses):
        await payments.capture(payment_intent_id)
        await send_booking_confirmation(order, smtp_client)
        return True

    if resources.OrderStatus.pending.value not in booking_statuses:
        await payments.cancel(payment_intent_id)
        return True

    return False


async def poll_order_status(
    junction_client: client.JunctionClient,
    order_id: str,
    payment_intent_id: str,
    smtp_client: smtp.EmailClient,
) -> bool:
    time_spent = 0
    while time_spent <= _ORDER_STATUS_POLLING_TIMEOUT:
        order = await junction_client.get_order_by_id(
            identifier=order_id,
            include=["bookings"],
        )
        payment_processed = await _handle_new_order_results(
            payment_intent_id,
            order,
            smtp_client,
        )
        if payment_processed:
            return True

        await asyncio.sleep(_ORDER_STATUS_POLLING_INTERVAL)
        time_spent += _ORDER_STATUS_POLLING_INTERVAL

    await payments.cancel(payment_intent_id)
    return False


# TODO: refactor using includes
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
