import dataclasses
import datetime

from snowfall.vendor.save_a_train.models import booking


@dataclasses.dataclass(frozen=True)
class SearchResultRequirement:
    departure_datetime: datetime.datetime
    arrival_datetime: datetime.datetime


@dataclasses.dataclass(frozen=True)
class CombinedBookingResults:
    make_booking: booking.BookingResult
    confirm_booking: booking.BookingConfirmationResult
    get_ticket: booking.TicketInfo
