from pydantic import Field
from pydantic.json_schema import SkipJsonSchema

from snowfall.project.fti.service.bigxtra_api.models import (
    BaseModel,
    PaginationQueryParams,
)


class PlaceModel(BaseModel):
    name: str = Field(json_schema_extra={"example": "Athens"})
    country: str = Field(json_schema_extra={"example": "Greece"})
    latitude: float = Field(json_schema_extra={"example": 90.0})
    longitude: float = Field(json_schema_extra={"example": 180.0})
    iata_code: str | SkipJsonSchema[None] = Field(
        default=None,
        json_schema_extra={"nullable": True, "example": "ATH"},
    )


class PlacesModel(BaseModel):
    places: list[PlaceModel]


class PlacesQueryParams(BaseModel):
    destination: str | SkipJsonSchema[None] = Field(
        default=None,
        json_schema_extra={
            "example": "ATH",
            "description": "If set, the endpoint returns places connected to this destination place.",
        },
    )


class FlightModel(BaseModel):
    origin: PlaceModel
    destination: PlaceModel
    departure_at: str = Field(json_schema_extra={"format": "date-time"})
    arriving_at: str = Field(json_schema_extra={"format": "date-time"})
    airline: str = Field(json_schema_extra={"example": "AA"})
    cancellation_policy: str = Field(json_schema_extra={"example": "Flexible"})
    tour_operator: str = Field(json_schema_extra={"example": "FTI tours"})


class ReviewModel(BaseModel):
    user_id: str = Field(json_schema_extra={"format": "uuid"})
    details: str = Field(json_schema_extra={"example": "It was ok"})
    rating: float = Field(json_schema_extra={"example": 4.0})


class AccommodationRoomModel(BaseModel):
    room_label: str = Field(json_schema_extra={"example": "Double room"})
    num_of_guests: int = Field(json_schema_extra={"example": 2})
    sea_view: bool = Field(json_schema_extra={"example": False})
    included_meal_options: list[str] = Field(
        json_schema_extra={"example": ["All inclusive"]},
    )


class AccommodationModel(BaseModel):
    type: str = Field(json_schema_extra={"example": "Hotel"})
    address: str = Field(json_schema_extra={"example": "Miracle street 69"})
    category: int = Field(json_schema_extra={"example": 4})
    rating: float = Field(json_schema_extra={"example": 3.8})
    location: PlaceModel
    rooms: list[AccommodationRoomModel]
    services: list[str] = Field(json_schema_extra={"example": ["Pool", "Transfer"]})
    reviews: list[ReviewModel]
    cancellation_policy: str = Field(json_schema_extra={"example": "Flexible"})
    cms_info: str = Field(json_schema_extra={"example": "Photos URL and stuff"})
    tour_operator: str = Field(json_schema_extra={"example": "FTI tours"})


class AccommodationsModel(BaseModel):
    accommodations: list[AccommodationModel]


class AccommodationOffersQueryParams(PaginationQueryParams):
    destination: str = Field(json_schema_extra={"example": "Athens"})
    arrive_at: str = Field(
        json_schema_extra={
            "format": "date",
            "description": "Starting date of the trip",
        },
    )
    return_at: str = Field(
        json_schema_extra={
            "format": "date",
            "description": "Returning date of the trip",
        },
    )
    num_of_guests: int = Field(
        le=4,
        ge=1,
        json_schema_extra={
            "example": 3,
        },
    )


class PackageModel(BaseModel):
    outbound: FlightModel
    inbound: FlightModel
    price: float = Field(json_schema_extra={"example": 120.0})
    tour_operator: str = Field(json_schema_extra={"example": "FTI tours"})
    accommodation: AccommodationModel
    tags: list[str] = Field(
        json_schema_extra={"example": ["beach", "family", "sports"]},
    )


class PackagesModel(BaseModel):
    packages: list[PackageModel]


class PackageOffersQueryParams(AccommodationOffersQueryParams):
    origin: str = Field(json_schema_extra={"example": "London"})
