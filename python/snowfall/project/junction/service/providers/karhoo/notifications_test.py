from typing import Any
from unittest import mock

import freezegun
import pytest

from snowfall.project.junction.go.service.orders.v1alpha import amqp_pb2
from snowfall.project.junction.service.providers.karhoo import notifications
from snowfall.vendor.karhoo.models import bookings, location

_FREEZE_DATE = "2022-05-24T13:37:00+00:00"
_ORDER_ID = "ORDER_ID"
_BOOKING_ID = "FOOBAR"
_FOLLOW_CODE = "ABCDEF"
_PICKUP_POINT_LATITUDE = "3.18648"
_PICKUP_POINT_LONGITUDE = "30.78786"
_ORIGIN_LOCATION = "Somewhere lane"
_DESTINATION_LOCATION = "Somewhere else lane"
_FIRST_NAME = "First"
_LAST_NAME = "Last"
_CONFIRMED_STATUS = "CONFIRMED"
_METADATA = amqp_pb2.OrderMetadata(
    journey_id="JOURNEY_ID",
    order_id="ORDER_ID",
    booking_id="BOOKING_ID",
    passenger_name_record="FOOBAR",
)


def _get_mocked_booking() -> bookings.BookingResponse:
    booking = mock.create_autospec(bookings.BookingResponse)
    booking.id = _BOOKING_ID
    booking.follow_code = _FOLLOW_CODE
    booking.date_scheduled = _FREEZE_DATE
    booking.origin = mock.create_autospec(location.Place)
    booking.origin.position = mock.create_autospec(location.Position)
    booking.origin.position.latitude = _PICKUP_POINT_LATITUDE
    booking.origin.position.longitude = _PICKUP_POINT_LONGITUDE
    booking.origin.display_address = _ORIGIN_LOCATION
    booking.destination = mock.create_autospec(location.Place)
    booking.destination.display_address = _DESTINATION_LOCATION
    booking.destination.position = mock.create_autospec(location.Position)

    return booking


def test_booking_notification_subject() -> None:
    booking_reference = "FOOBAR"
    booking = mock.create_autospec(bookings.BookingResponse)
    booking.id = booking_reference
    notification = notifications.BookingNotification(_METADATA, booking)
    assert notification.subject.endswith(booking_reference)


@freezegun.freeze_time(_FREEZE_DATE)
@pytest.mark.parametrize(
    ("body_field", "expected"),
    [
        ("journey id", _METADATA.journey_id),
        ("order id", _METADATA.order_id),
        ("booking id", _METADATA.booking_id),
        ("spnr", _METADATA.passenger_name_record),
        ("booking date", _FREEZE_DATE),
        ("follow code", _FOLLOW_CODE),
        ("pickup date", _FREEZE_DATE),
        ("pickup point latitude", _PICKUP_POINT_LATITUDE),
        ("pickup point longitude", _PICKUP_POINT_LONGITUDE),
        ("start location", _ORIGIN_LOCATION),
        ("destination location", _DESTINATION_LOCATION),
    ],
)
def test_booking_notification_body(body_field: str, expected: Any) -> None:
    notification = notifications.BookingNotification(_METADATA, _get_mocked_booking())

    split_lines = (
        line.split(" : ")
        for line in notification.body.splitlines()
        if line.count(" : ")
    )
    lines = {field.lower(): field_value for field, field_value in split_lines}
    assert lines[body_field] == expected
