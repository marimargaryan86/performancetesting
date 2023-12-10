from collections.abc import Mapping, Sequence
from typing import Any

from snowfall.stdlib import money
from snowfall.vendor.zendesk.models import (
    cancellation_request as cancellation_request_models,
)


def parse_cancellation_request_models(
    booking: cancellation_request_models.Booking,
    order: cancellation_request_models.Order,
    journey: cancellation_request_models.Journey,
    refunded_us: money.Money | None = None,
    *,
    convert_to_html: bool = True,
) -> dict[str, Any] | str:
    parsed_details = {
        "Booking ID": booking.booking_id,
        "Order ID": order.order_id,
        "Reseller ID": journey.reseller_id,
        "Super PNR": journey.passenger_name_record,
        "Provider Name": booking.provider_name,
        "Trip Reference": booking.trip_reference,
        "Operator Booking References": _parse_operator_booking_references(
            booking.operator_booking_references,
        ),
        "Total Price": "{0} {1}".format(
            booking.price.amount,
            booking.price.currency,
        ),
        "Passengers": _parse_passengers(order.passengers),
        "Trip Details": _parse_trip_options(booking.trip_options),
    }

    if refunded_us:
        parsed_details["Refunded Amount"] = "{0} {1}".format(
            refunded_us.amount,
            refunded_us.currency,
        )

    if convert_to_html:
        return _dict_to_html_ul(parsed_details)

    return parsed_details


def _parse_operator_booking_references(
    booking_references: Sequence[cancellation_request_models.OperatorBookingReference],
) -> list[dict[str, Any]]:
    return [
        {
            "Operator Booking Reference": booking_ref.operator_booking_reference,
        }
        for booking_ref in booking_references
    ]


def _parse_passengers(
    passengers: Sequence[cancellation_request_models.Passengers],
) -> list[dict[str, Any]]:
    return [
        {
            "Name": "{0}, {1}".format(
                passenger.last_name,
                passenger.first_name,
            ),
        }
        for passenger in passengers
    ]


def _parse_trip_options(
    trip_options: Sequence[cancellation_request_models.Segment],
) -> list[dict[str, Any]]:
    return [
        {
            "Segment": {
                "Operator": trip_option.operator,
                "Legs": _parse_legs(trip_option.legs),
            },
        }
        for trip_option in trip_options
    ]


def _parse_legs(
    legs: Sequence[cancellation_request_models.Leg],
) -> list[dict[str, Any]]:
    return [
        {
            "Leg": {
                "Route": "{0} --> {1}".format(
                    leg.origin_name,
                    leg.destination_name,
                ),
                "Departure Date": leg.departure_date,
            },
        }
        for leg in legs
    ]


def _dict_to_html_ul(dict_to_convert: Mapping[str, Any]) -> str:
    html = ["<ul>"]

    for key, item_val in dict_to_convert.items():
        html.append("<li><b>{0}</b>: ".format(key))
        if isinstance(item_val, dict):
            html.append(
                "{0}</li>".format(
                    _dict_to_html_ul(item_val),
                ),
            )
        elif isinstance(item_val, list):
            html = [
                *html,
                *["{0}</li>".format(_dict_to_html_ul(seq)) for seq in item_val],
            ]
        else:
            html.append("{0}</li>".format(item_val))
    html.append("</ul>")

    return "".join(html)
