from __future__ import annotations

from snowfall.vendor.ba_ndc.models.request_offer_search_schemas import (
    OfferSearchRequest,
    Passenger,
    Trip,
)
from snowfall.vendor.ba_ndc.models.util import offer_enums, passenger_enums


class OffersRequestBuilder(object):
    def __init__(self) -> None:
        self._passengers: list[Passenger] = []
        self._trips: list[Trip] = []
        self._cabin_type = offer_enums.CabinTypeEnum.economy

    def set_cabin(self, cabin_type: offer_enums.CabinTypeEnum) -> OffersRequestBuilder:
        self._cabin_type = cabin_type
        return self

    def add_passenger(
        self,
        passenger_type: passenger_enums.PassengerTypeEnum,
    ) -> OffersRequestBuilder:
        passenger = Passenger(
            passenger_type=passenger_type,
            birth_date=None,
        )
        self._passengers.append(passenger)
        return self

    def add_trip(self, trip: Trip) -> OffersRequestBuilder:
        self._trips.append(trip)
        return self

    def build(self) -> OfferSearchRequest:
        return OfferSearchRequest(
            cabin_type=self._cabin_type,
            fare_preferences={
                offer_enums.FareGroupEnum.fare_rules,
            },
            passengers=self._passengers,
            trips=self._trips,
        )
