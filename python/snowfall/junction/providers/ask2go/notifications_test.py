import datetime
from typing import Any
from unittest import mock

import freezegun
import pytest

from snowfall.junction.orders.v1alpha import models_pb2
from snowfall.junction.providers.ask2go import notifications
from snowfall.vendor.ask2go.models import booking as a2g_booking
from snowfall.vendor.ask2go.models import offers

_FREEZE_DATE = "2022-05-24T13:37:00+00:00"
_BOOKING_REFERENCE = "FOOBAR"
_PNR_REFERENCE = "BAZQUX"
_FIRST_NAME = "First"
_LAST_NAME = "Last"
_TRAVEL_DATE = datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)
_ORDER = models_pb2.Order(id="123", passenger_name_record="ABCDEF")


def _get_mocked_booking() -> a2g_booking.Booking:
    booking = mock.create_autospec(a2g_booking.Booking)
    booking.information = mock.create_autospec(a2g_booking.Information)
    booking.information.check_in_locators = [_BOOKING_REFERENCE]
    booking.information.record_locators = [_PNR_REFERENCE]
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
    notification = notifications.BookingNotification(models_pb2.Order(), booking)
    assert notification.subject.endswith(booking_reference)


@freezegun.freeze_time(_FREEZE_DATE)
@pytest.mark.parametrize(
    "body_field, expected",
    [
        ("order", _ORDER.id),
        ("spnr", _ORDER.passenger_name_record),
        ("record", _BOOKING_REFERENCE),
        ("checkin", _PNR_REFERENCE),
        ("first", _FIRST_NAME),
        ("last", _LAST_NAME),
        ("booking", _FREEZE_DATE),
        ("travel", _TRAVEL_DATE.isoformat(timespec="seconds")),
    ],
)
def test_booking_notification_body(body_field: str, expected: Any) -> None:
    notification = notifications.BookingNotification(_ORDER, _get_mocked_booking())
    split_lines = (
        line.split(" : ")
        for line in notification.body.splitlines()
        if line.count(" : ")
    )
    lines = {
        field.split(" ")[0].lower(): field_value for field, field_value in split_lines
    }
    assert lines[body_field] == expected
