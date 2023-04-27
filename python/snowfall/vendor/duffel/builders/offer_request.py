from __future__ import annotations

import datetime

import pydantic

from snowfall.vendor.duffel.builders.base import DuffelRequestBaseModel
from snowfall.vendor.duffel.models.offer import Offer


class OfferRequestSliceTimeRange(DuffelRequestBaseModel):
    time_from: str = pydantic.Field(alias="from")
    to: str


class OfferRequestSlice(DuffelRequestBaseModel):
    destination: str
    origin: str
    departure_date: datetime.date
    arrival_time: OfferRequestSliceTimeRange | None
    departure_time: OfferRequestSliceTimeRange | None


class LoyaltyProgrammeAccount(DuffelRequestBaseModel):
    airline_iata_code: str
    account_number: str


class OfferRequestPassenger(DuffelRequestBaseModel):
    age: int | None
    pax_type: str | None = pydantic.Field(alias="type")
    given_name: str | None
    family_name: str | None
    loyalty_programme_accounts: list[LoyaltyProgrammeAccount] | None


class OfferRequestDataList(DuffelRequestBaseModel):
    passengers: list[OfferRequestPassenger]
    slices: list[OfferRequestSlice]


class OfferRequestData(DuffelRequestBaseModel):
    offer_data: OfferRequestDataList = pydantic.Field(alias="data")


class OffersRequestBuilder(object):
    def __init__(self) -> None:
        self._passengers: list[OfferRequestPassenger] = []
        self._slices: list[OfferRequestSlice] = []

    def with_offer(self, offer: Offer) -> OffersRequestBuilder:
        for passenger in offer.passengers:
            self.add_passenger(
                OfferRequestPassenger(
                    pax_type=passenger.passenger_type,
                    age=passenger.age,
                ),
            )

        for offer_slice in offer.slices:
            first_segment = offer_slice.segments[0]
            last_segment = offer_slice.segments[-1]
            self.add_slice(
                OfferRequestSlice(
                    destination=last_segment.destination.iata_code or "",
                    origin=first_segment.origin.iata_code or "",
                    departure_date=first_segment.departing_at.date(),
                    departure_time=OfferRequestSliceTimeRange(
                        time_from=first_segment.departing_at.strftime("%H:%M"),
                        to=(
                            first_segment.departing_at + datetime.timedelta(minutes=1)
                        ).strftime("%H:%M"),
                    ),
                    arrival_time=OfferRequestSliceTimeRange(
                        time_from=last_segment.arriving_at.strftime("%H:%M"),
                        to=(
                            last_segment.arriving_at + datetime.timedelta(minutes=1)
                        ).strftime("%H:%M"),
                    ),
                ),
            )

        return self

    def add_passenger(self, passenger: OfferRequestPassenger) -> OffersRequestBuilder:
        self._passengers.append(passenger)
        return self

    def add_slice(self, route: OfferRequestSlice) -> OffersRequestBuilder:
        self._slices.append(route)
        return self

    def build(self) -> OfferRequestData:
        return OfferRequestData(
            offer_data=OfferRequestDataList(
                passengers=self._passengers,
                slices=self._slices,
            ),
        )
