from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict, alias_generators


class CamelCaseBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=alias_generators.to_camel,
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class UTCAndLocalDates(CamelCaseBaseModel):
    date_utc: str
    date_local: str


class FlightStatusOperationalTimes(CamelCaseBaseModel):
    scheduled_gate_departure: UTCAndLocalDates
    estimated_gate_departure: UTCAndLocalDates


class AirportResources(CamelCaseBaseModel):
    departure_terminal: str
    departure_gate: str
    arrival_terminal: str
    arrival_gate: str
    baggage: str


class FlightStatus(CamelCaseBaseModel):
    status: str
    operational_times: FlightStatusOperationalTimes
    airport_resources: AirportResources


class Airport(CamelCaseBaseModel):
    name: str


class Delay(CamelCaseBaseModel):
    departure_runway_delay_minutes: int
    departure_gate_delay_minutes: int


class GetFlightStatusResponse(CamelCaseBaseModel):
    airports: Sequence[Airport]
    flight_statuses: Sequence[FlightStatus]
    delays: Delay
