from collections.abc import Mapping, Sequence

from pydantic import BaseModel, ConfigDict, alias_generators


class CamelCaseBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=alias_generators.to_camel,
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class Flight(CamelCaseBaseModel):
    origin: str
    destination: str
    operating_carrier_code: str
    flight_number: int
    departure_date: Mapping[str, int]

    def __hash__(self) -> int:
        departure_date_hashable = tuple(sorted(self.departure_date.items()))
        hashable_components = (
            self.operating_carrier_code,
            self.flight_number,
            departure_date_hashable,
        )

        return hash(hashable_components)


class Emission(CamelCaseBaseModel):
    first: int
    business: int
    premium_economy: int
    economy: int


class FlightEmission(CamelCaseBaseModel):
    flight: Flight
    emissions_grams_per_pax: Emission | None = None


class GetEmissionsResponse(CamelCaseBaseModel):
    flight_emissions: Sequence[FlightEmission]
