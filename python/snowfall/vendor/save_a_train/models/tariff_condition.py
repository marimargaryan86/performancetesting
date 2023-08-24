from pydantic.v1 import BaseModel


class Condition(BaseModel):
    name: str
    description: str


class TariffCondition(BaseModel):
    name: str
    conditions: list[Condition]


class TariffConditionsResponse(BaseModel):
    result_id: int
    search_identifier: str
    result_fare_id: int
    tariff_conditions: TariffCondition
