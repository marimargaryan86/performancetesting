import datetime
import uuid

from pydantic import v1 as pydantic

from snowfall.stdlib import money


class CamelCaseBaseModel(pydantic.BaseModel):
    class Config(object):
        allow_population_by_field_name = True
        extra = pydantic.Extra.forbid


class Payment(CamelCaseBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    amount: float
    failure_returned_amount: float
    beneficiary_id: uuid.UUID
    conversion_id: uuid.UUID | None
    currency: money.Currency
    reference: str
    reason: str
    status: str
    payment_type: str
    payment_date: datetime.datetime
    transferred_at: datetime.datetime | None
    authorisation_steps_required: int
    creator_contact_id: uuid.UUID
    last_updater_contact_id: uuid.UUID
    short_reference: str
    failure_reason: str
    payment_group_id: uuid.UUID | None
    unique_request_id: str
