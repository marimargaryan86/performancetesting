import datetime
import uuid

import pydantic

from snowfall.stdlib import money


class Payment(pydantic.BaseModel):
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
