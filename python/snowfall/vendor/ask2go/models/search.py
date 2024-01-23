import datetime
import uuid

from snowfall.vendor.ask2go.enums import AirCabinClassType
from snowfall.vendor.ask2go.models import offers
from snowfall.vendor.ask2go.models.base import CamelCaseBaseModel


class CreateSearchResponse(CamelCaseBaseModel):
    id: str
    transaction_id: str


class SearchResultsPageInformation(CamelCaseBaseModel):
    current_page: int
    total_pages: int
    number_of_available_flights: int


class SearchResultsResponse(CamelCaseBaseModel):
    id: str
    available_flights: int
    flight: list[offers.Offer]
    is_finished: bool
    page_information: SearchResultsPageInformation
    transaction_id: str


class CreateSearchCriteria(CamelCaseBaseModel):
    origin_iata: str
    destination_iata: str
    outbound_date: datetime.datetime | datetime.date
    affiliate_id: int | None = None
    outbound_departure_window: tuple[datetime.time, datetime.time] | None = None
    inbound_date: datetime.datetime | datetime.date | None = None
    inbound_departure_window: tuple[datetime.time, datetime.time] | None = None
    cabin_class: AirCabinClassType = AirCabinClassType.any_
    adults: int = 0
    children: int = 0
    infants: int = 0
    transaction_id: uuid.UUID | None = None
