from pydantic.v1 import Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.payment import Price
from snowfall.vendor.benerail.models.bookings.train import Flexibility, TrainType
from snowfall.vendor.benerail.models.products.product import ComfortClass
from snowfall.vendor.benerail.models.trip_offers.features import (
    AccommodationType,
    BookableStatus,
)


class TripSummary(BenerailBaseModel):
    departure_at: str | None = Field(
        None,
        description="ISO-8601 timestamp showing date time and timezone of departure",
        example="2021-09-29T13:20:34.143+02:00",
    )
    arrival_at: str | None = Field(
        None,
        description="ISO-8601 timestamp showing date time and timezone of departure",
        example="2021-09-29T13:20:34.143+02:00",
    )
    number_of_transfers: float | None = Field(
        None,
        description="Number of interchanges",
        example=1,
    )
    duration: str | None = Field(
        None,
        description="Overall duration of the trip",
        example="PT20M",
    )
    train_types: list[TrainType] | None


class ProductSummary(BenerailBaseModel):
    taco: str | None = None
    flexibility: Flexibility | None = None
    comfort_class: ComfortClass | None = None


class OfferSummary(BenerailBaseModel):
    price_with_optional_parts: Price
    price_without_optional_parts: Price | None = None
    total_price: Price | None = None
    flexibility: Flexibility | None = None
    comfort_class: ComfortClass | None = None
    accommodation_type: AccommodationType | None = None


class OfferPartSummaryProduct(BenerailBaseModel):
    taco: str | None = None


class OfferPartSummary(BenerailBaseModel):
    product: OfferPartSummaryProduct | None = None
    accommodation_type: AccommodationType | None = None


class TripOfferSummary(BenerailBaseModel):
    cheapest_first_class_with_optional_parts: Price | None = None
    cheapest_second_class_with_optional_parts: Price | None = None
    cheapest_price_without_optional_parts: Price | None = None
    related_trip_id: str | None = None
    bookable_status: BookableStatus
    accommodation_type: AccommodationType | None = None


class PassengerResourceLinkSummary(BenerailBaseModel):
    age_category: str | None = None
    cards: str | None = None
    corporate_contracts: str | None = None
