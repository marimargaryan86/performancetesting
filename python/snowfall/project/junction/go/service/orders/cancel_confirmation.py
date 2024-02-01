import datetime
from collections.abc import Iterable
from typing import Any

import aiofiles
import jinja2

from snowfall.project.junction.go.service.orders import smtp
from snowfall.project.junction.go.service.orders.v1 import models_pb2
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence import filesystem


class EnvironmentURLs(object):
    development_url = "https://hub.junction.dev/"
    sandbox_url = "https://hub.sandbox.junction.dev/"
    production_url = "https://hub.junction.travel/"

    @classmethod
    def get_url(cls, environment: str) -> str:
        return {
            "development": cls.development_url,
            "sandbox": cls.sandbox_url,
            "production": cls.production_url,
        }.get(environment, cls.development_url)


def format_datetime(original_datetime_str: str) -> str:
    original_datetime = datetime.datetime.fromisoformat(
        original_datetime_str.replace("Z", "+00:00"),
    )

    return original_datetime.strftime("%A %d %b %Y %H:%M")


def _order_details_sorted_by_date(
    details: Iterable[models_pb2.TripOptionDetails],
) -> list[dict[str, Any]]:
    detail_objects = [
        {
            "origin": leg.origin.name,
            "destination": leg.destination.name,
            "departure_at": protobuf.protobuf_to_datetime(leg.departure_at),
            "arrival_at": protobuf.protobuf_to_datetime(leg.arrival_at),
            "ref": detail.segment.vendor,
            "leg_type": detail.segment.type,
        }
        for detail in details
        for leg in detail.segment.legs
    ]

    return sorted(detail_objects, key=lambda detail: detail["departure_at"])


async def send_cancel_confirmation(
    journey: models_pb2.Journey,
    order: models_pb2.Order,
    booking: models_pb2.Booking,
    smtp_client: smtp.EmailClient,
    booking_cancellation_status: models_pb2.BookingCancellation.Status.ValueType,
    environment: str,
    *,
    forward_email: str | None = None,
) -> None:
    total_price = money.from_protobuf(booking.total_price)
    base_url = EnvironmentURLs.get_url(environment)

    full_link = "{link}trip-management/orders/{order_id}/{booking_id}".format(
        link=base_url,
        order_id=order.id,
        booking_id=booking.id,
    )
    details = _order_details_sorted_by_date(booking.trip_option.details)
    template_path = filesystem.resource_path(
        "snowfall.project.junction.go.service.orders.html_templates",
        "booking_cancel_template.html",
    )
    async with aiofiles.open(template_path) as template_file:
        template_content = await template_file.read()
    body = jinja2.Template(template_content).render(
        details=details,
        full_link=full_link,
        reference=journey.passenger_name_record,
        status=" ".join(
            word.capitalize()
            for word in protobuf.enum_value_to_slug(
                models_pb2.BookingCancellation.Status.DESCRIPTOR,
                booking_cancellation_status,
            ).split("-")
        ),
        passengers=list(order.passengers),
        total_price=str(total_price),
        currency=booking.total_price.currency_code,
        record_locators=booking.trip_result.record_locator,
        operator_booking_references=booking.trip_result.operator_booking_references,
    )

    email_recipient = forward_email or journey.contact_details.email
    email_subject = "Cancellation details for Booking {pnr}".format(
        pnr=journey.passenger_name_record,
    )

    await smtp_client.send_email_html_template(email_recipient, email_subject, body)
