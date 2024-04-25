from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from enum import Enum
from typing import ClassVar, Literal

from pydantic import AwareDatetime, Field

from snowfall.project.junction.rocket.service.api.models import BaseModel
from snowfall.stdlib.integration.starlette import (
    models,
)


class StatusTypeEnum(Enum):
    """Status Types."""

    unspecified: str = "unspecified"
    pending: str = "pending"
    processing: str = "processing"
    completed: str = "completed"
    failed: str = "failed"


class FareTypeEnum(Enum):
    """Offer Fare Types."""

    basic: str = "1"
    standard: str = "2"
    enhanced: str = "3"
    premium: str = "4"
    premium_plus: str = "5"
    lux: str = "6"


class Passenger(BaseModel):
    date_of_birth: date


class FlightSearchAttributes(BaseModel):
    departure_after: datetime
    return_at: datetime | None = None
    passengers: list[Passenger]


class SelectedOutboundOfferData(BaseModel):
    id: str
    type: Literal["flight-offers"]


class SelectedOutboundOffer(BaseModel):
    data: SelectedOutboundOfferData


class PlaceIdentifier(BaseModel):
    id: str
    type: str


class PlaceContainer(BaseModel):
    data: PlaceIdentifier


class FlightSearchRelationships(BaseModel):
    selected_outbound_offer: SelectedOutboundOffer | None = None
    origin: PlaceContainer
    destination: PlaceContainer


class FlightSearchRequestData(BaseModel):
    type: Literal["flight-searches"]
    attributes: FlightSearchAttributes
    relationships: FlightSearchRelationships


class FlightSearchRequest(BaseModel):
    data: FlightSearchRequestData


class SearchCapabilities(BaseModel):
    rail: bool
    air: bool
    ferry: bool


class ResultDetails(BaseModel):
    id: str = Field(..., alias="_id")
    flight_number: str
    marketing_airline: str
    arrival_station: str
    departure_station: str
    departure_at: AwareDatetime
    arrival_at: AwareDatetime
    duration: int
    segment_key: str
    operating_airline: str


class Price(BaseModel):
    price: float
    currency: str


class CabinDetails(BaseModel):
    id: str = Field(alias="uid")
    result_detail_id: str | None = Field(..., alias="resultDetail")
    marketing_name: str | None


class Offer(BaseModel):
    id: str = Field(..., alias="_id")
    price: Price
    fare_type: FareTypeEnum
    name: str
    cabin_details: list[CabinDetails]
    ref_ids: list[str]


class FlightSearchResult(BaseModel):
    id: str = Field(..., alias="_id")
    search_id: str
    provider_id: str
    offers: list[Offer]
    result_details: list[ResultDetails]


def now_factory() -> datetime:
    return datetime.now(tz=UTC)


def expires_factory() -> datetime:
    return now_factory() + timedelta(hours=1)


class FlightSearchRequestStorage(BaseModel):
    search_id: str
    reseller_id: str
    expires_at: datetime = Field(default_factory=expires_factory)
    created_at: datetime = Field(default_factory=now_factory)
    updated_at: datetime = Field(default_factory=now_factory)
    flight: FlightSearchAttributes


class FlightSearchResponseAttributes(FlightSearchAttributes):
    status: StatusTypeEnum
    expires_at: str


class FlightSearchResultResource(models.Resource):
    api_type: ClassVar[str] = "flight-search-results"

    @classmethod
    def from_model(
        cls,
        search_result: FlightSearchResult,
        search: FlightSearchRequestStorage,
    ) -> FlightSearchResultResource:
        expires_at = search.expires_at.isoformat()
        return cls(
            id=search_result.id,
            type="flight-search-results",
            attributes={"expiresAt": expires_at},
            relationships={
                "offers": {
                    "data": [
                        OfferResource.from_model(offer)
                        for offer in search_result.offers
                    ],
                },
                "resultDetails": {
                    "data": [
                        ResultDetailResource.from_model(result_details)
                        for result_details in search_result.result_details
                    ],
                },
                "search": {
                    "data": SearchResource.from_model(search),
                },
            },
        )


class SearchResource(models.Resource):
    api_type: ClassVar[str] = "flight-searches"

    @classmethod
    def from_model(cls, search: FlightSearchRequestStorage) -> SearchResource:
        return cls(
            id=search.search_id,
            type=SearchResource.api_type,
        )


class ResultDetailResource(models.Resource):
    api_type: ClassVar[str] = "flight-result-details"

    @classmethod
    def from_model(cls, result_detail: ResultDetails) -> ResultDetailResource:
        return cls(
            id=result_detail.id,
            type=ResultDetailResource.api_type,
            attributes={
                "flightNumber": result_detail.flight_number,
                "marketingAirline": result_detail.marketing_airline,
                "arrivalStation": result_detail.arrival_station,
                "departureStation": result_detail.departure_station,
                "departureTime": result_detail.departure_at,
                "arrivalTime": result_detail.arrival_at,
                "duration": result_detail.duration,
                "operatingAirline": result_detail.operating_airline,
            },
        )


class OfferResource(models.Resource):
    api_type: ClassVar[str] = "flight-offers"

    @classmethod
    def from_model(cls, offer: Offer) -> OfferResource:
        return cls(
            id=offer.id,
            type=OfferResource.api_type,
            attributes={
                "price": {
                    "currency": offer.price.currency,
                    "amount": str(offer.price.price),
                },
                "fareType": offer.fare_type.name.replace("_", "-"),
                "name": offer.name,
                "cabinDetails": [
                    {
                        "resultDetail": cabin_detail.result_detail_id,
                        "marketingName": cabin_detail.marketing_name,
                    }
                    for cabin_detail in offer.cabin_details
                ],
            },
        )
