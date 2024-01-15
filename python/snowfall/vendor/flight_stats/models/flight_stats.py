import datetime
from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict, alias_generators


class CamelCaseBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=alias_generators.to_camel,
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class UTCAndLocalDates(CamelCaseBaseModel):
    date_utc: datetime.datetime
    date_local: datetime.datetime


class FlightStatusOperationalTimes(CamelCaseBaseModel):
    scheduled_gate_departure: UTCAndLocalDates
    estimated_gate_departure: UTCAndLocalDates


class AirportResources(CamelCaseBaseModel):
    departure_terminal: str | None = None
    departure_gate: str | None = None
    arrival_terminal: str | None = None
    arrival_gate: str | None = None
    baggage: str | None = None


class Delay(CamelCaseBaseModel):
    departure_gate_delay_minutes: int
    arrival_gate_delay_minutes: int


class FlightStatus(CamelCaseBaseModel):
    status: str
    operational_times: FlightStatusOperationalTimes
    airport_resources: AirportResources
    flight_number: str
    carrier_fs_code: str
    flight_id: int
    delays: Delay


class GetFlightStatusResponse(CamelCaseBaseModel):
    flight_statuses: Sequence[FlightStatus]


class Error(CamelCaseBaseModel):
    http_status_code: int
    error_id: str
    error_message: str
    error_code: str
