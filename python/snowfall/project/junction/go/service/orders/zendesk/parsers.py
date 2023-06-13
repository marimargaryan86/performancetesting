from collections.abc import Mapping
from typing import Any

from snowfall.project.junction.go.service.offers.v1alpha.models_pb2 import OfferSegment
from snowfall.project.junction.go.service.orders.v1alpha import models_pb2
from snowfall.stdlib import money
from snowfall.stdlib.format.protobuf import protobuf_to_datetime


def parse_booking_and_order_for_cancel_request(
    booking: models_pb2.Booking,
    order: models_pb2.Order,
    journey: models_pb2.Journey,
    convert_to_html: bool = True,
) -> dict[str, Any] | str:
    total_price = money.from_protobuf(booking.total_price)
    parsed_details = {
        "Booking ID": booking.id,
        "Order ID": order.id,
        "Reseller ID": journey.reseller_id,
        "Super PNR": journey.passenger_name_record,
        "Provider Name": booking.provider_name,
        "Trip Reference": booking.trip_result.record_locator,
        "Operator Booking References": _parse_operator_booking_references(booking),
        "Total Price": "{0} {1}".format(
            str(total_price),
            total_price.currency.code,
        ),
        "Passengers": _parse_passengers(order),
        "Trip Details": _parse_trip_options(booking),
    }

    if convert_to_html:
        return _dict_to_html_ul(parsed_details)

    return parsed_details


def _parse_operator_booking_references(
    booking: models_pb2.Booking,
) -> list[dict[str, Any]]:
    return [
        {
            "Operator Booking Reference": booking_ref,
        }
        for booking_ref in booking.trip_result.operator_booking_references
    ]


def _parse_passengers(order: models_pb2.Order) -> list[dict[str, Any]]:
    return [
        {
            "Name": "{0}, {1}".format(
                passenger.last_name,
                passenger.first_name,
            ),
        }
        for passenger in order.passengers
    ]


def _parse_trip_options(
    booking: models_pb2.Booking,
) -> list[dict[str, Any]]:
    return [
        {
            "Segment": {
                "Operator": trip_option.segment.operator,
                "Legs": _parse_legs(trip_option.segment),
            },
        }
        for trip_option in booking.trip_option.details
    ]


def _parse_legs(segment: OfferSegment) -> list[dict[str, Any]]:
    return [
        {
            "Leg": {
                "Route": "{0} --> {1}".format(
                    leg.origin.name,
                    leg.destination.name,
                ),
                "Departure Date": str(protobuf_to_datetime(leg.departure_at)),
            },
        }
        for leg in segment.legs
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
            for seq in item_val:
                html.append("{0}</li>".format(_dict_to_html_ul(seq)))
        else:
            html.append("{0}</li>".format(item_val))
    html.append("</ul>")

    return "".join(html)
