import datetime
from typing import Any, Optional

from snowfall.vendor.ask2go.enums import AirCabinClassType
from snowfall.vendor.ask2go.models import offers
from snowfall.vendor.ask2go.models.base import CamelCaseBaseModel


class CreateSearchResponse(CamelCaseBaseModel):
    id: str  # noqa: A003
    transaction_id: str


class SearchResultsPageInformation(CamelCaseBaseModel):
    current_page: int
    total_pages: int
    number_of_available_flights: int


class SearchResultsResponse(CamelCaseBaseModel):
    id: str  # noqa: A003
    available_flights: int
    flight: list[offers.Offer]
    is_finished: bool
    filter_information: dict[str, Any]
    page_information: SearchResultsPageInformation
    transaction_id: str


class CreateSearchCriteria(CamelCaseBaseModel):
    origin_iata: str
    destination_iata: str
    outbound_date: datetime.date
    inbound_date: Optional[datetime.date]
    cabin_class: AirCabinClassType = AirCabinClassType.any_
    adults: int = 0
    children: int = 0
    infants: int = 0
