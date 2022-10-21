import asyncio
import datetime
from typing import Any, Mapping, Sequence

import aiofiles
import json_api_doc  # type: ignore[import]
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
    booking_statuses = {booking["status"]["id"] for booking in order["bookings"]}
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
        order = json_api_doc.deserialize(
            await junction_client.get_order_by_id(
                identifier=order_id,
                include=["journey", "bookings.details"],
            ),
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


async def send_booking_confirmation(
    order: Mapping[str, Any],
    smtp_client: smtp.EmailClient,
) -> None:
    details: Sequence[Mapping[str, Any]] = [
        detail for booking in order["bookings"] for detail in booking["details"]
    ]
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
        reference=order["journey"]["reference"],
        company_name=smtp_client.client_name,
        support_email=smtp_client.support_email,
        passengers=order["passengers"],
    )
    await smtp_client.send_email_html_template(
        order["journey"]["contactDetails"]["email"],
        "{company_name}. Itinerary details for Booking {reference}".format(
            company_name=smtp_client.client_name,
            reference=order["journey"]["reference"],
        ),
        body,
    )
    await smtp_client.send_email_html_template(
        smtp_client.support_email,
        "{company_name}. Itinerary details for Booking {reference}".format(
            company_name=smtp_client.client_name,
            reference=order["journey"]["reference"],
        ),
        body,
    )


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
            "legType": segment["legType"]["id"],
        }
        for segment in details
        for leg in segment["legs"]
    ]
    ordered_details.sort(key=lambda leg: leg["departureAt"])
    return ordered_details
