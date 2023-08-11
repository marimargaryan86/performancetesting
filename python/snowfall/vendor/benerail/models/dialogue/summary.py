from snowfall.vendor.benerail.models import types
from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.place import Place
from snowfall.vendor.benerail.models.trip_offers.link import PassengerResourceLink


class TripFilterSummary(BenerailBaseModel):
    origin: Place | None = None
    destination: Place | None = None
    departure_date_time: types.ZonedDatetimeStr | None = None


class TripOfferFilterSummary(BenerailBaseModel):
    origin: Place | None = None
    destination: Place | None = None
    departure_date_time: str | None = None
    passengers: list[PassengerResourceLink] | None = None
    is_return: bool | None = None


class BookerSummary(BenerailBaseModel):
    customer_name: str | None = None
    customer_number: str | None = None


class BookingSummary(BenerailBaseModel):
    first_departure_at: str | None = None
    contains_printed_tickets: bool | None = None
