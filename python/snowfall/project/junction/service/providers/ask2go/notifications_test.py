import datetime
from typing import Any
from unittest import mock

import freezegun
import pytest

from snowfall.project.junction.service.orders.v1alpha import amqp_pb2
from snowfall.project.junction.service.providers.ask2go import notifications
from snowfall.vendor.ask2go.models import booking as a2g_booking
from snowfall.vendor.ask2go.models import offers

_FREEZE_DATE = "2022-05-24T13:37:00+00:00"
_BOOKING_LOCATOR = "FOOBAR"
_CHECKIN_LOCATOR = "BAZQUX"
_FIRST_NAME = "First"
_LAST_NAME = "Last"
_TRAVEL_DATE = datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)
_METADATA = amqp_pb2.OrderMetadata(
    journey_id="JOURNEY_ID",
    order_id="ORDER_ID",
    booking_id="BOOKING_ID",
    passenger_name_record="FOOBAR",
)


def _get_mocked_booking() -> a2g_booking.Booking:
    booking = mock.create_autospec(a2g_booking.Booking)
    booking.information = mock.create_autospec(a2g_booking.Information)
    booking.information.record_locators = [_BOOKING_LOCATOR]
    booking.information.check_in_locators = [_CHECKIN_LOCATOR]
    booking.travelers = [{"firstName": _FIRST_NAME, "lastName": _LAST_NAME}]
    booking.air_itinerary = mock.create_autospec(offers.Offer)
    trip = mock.create_autospec(offers.Trip)
    trip.departure = mock.create_autospec(offers.TripDepartureArrival)
    trip.departure.date_time = _TRAVEL_DATE
    booking.air_itinerary.trips = [trip]

    return booking


def test_booking_notification_subject() -> None:
    booking_reference = "FOOBAR"
    booking = mock.create_autospec(a2g_booking.Booking)
    booking.information = mock.create_autospec(a2g_booking.Information)
    booking.information.check_in_locators = [booking_reference]
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
        ("record locator (sabre)", _BOOKING_LOCATOR),
        ("checkin locator (other)", _CHECKIN_LOCATOR),
        ("first name", _FIRST_NAME),
        ("last name", _LAST_NAME),
        ("booking date", _FREEZE_DATE),
        ("travel departure date", _TRAVEL_DATE.isoformat(timespec="seconds")),
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
