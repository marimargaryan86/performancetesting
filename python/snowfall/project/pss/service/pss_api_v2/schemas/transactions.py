import datetime
from enum import Enum
from typing import Literal

from pydantic import Field
from pydantic.class_validators import root_validator
from pydantic.networks import EmailStr

from snowfall.project.pss.service.pss_api_v2.schemas.schema import BaseSchema

EXTERNAL_REF_MAX_LENGTH = 255

Direction = Literal["outbound", "inbound"]


class PassengerType(int, Enum):  # noqa: WPS600 # Enable values in Swagger
    adult = 1
    senior = 2
    youth = 3
    child = 4
    campaign = 5
    student = 6
    infant = 7
    child_young = 8


class TransactionPassengerSchema(BaseSchema):
    passenger_type_id: PassengerType | None
    seat_id: int
    seat_type_id: int | None
    email: EmailStr | None


class TransactionDirectionSchema(BaseSchema):
    date: datetime.date | None
    destination_id: int
    origin_id: int
    schedule_id: int | None
    product_id: int | None
    passengers: list[TransactionPassengerSchema] = []


class TransactionPostSchema(BaseSchema):
    directions: set[Direction]
    channel: str
    outbound: TransactionDirectionSchema | None
    inbound: TransactionDirectionSchema | None
    amount: float | None
    net: float | None
    vat: float | None
    locale: str | None
    token: str | None
    transaction_status_id: int | None
    external_reference: str | None = Field(None, max_length=EXTERNAL_REF_MAX_LENGTH)
    customer_id: int | None
    account_id: int | None
    booking_id: int | None
    agreement_id: int | None

    @root_validator()
    def check_outbound_or_inbound(cls, values):  # type: ignore[no-untyped-def] # noqa: B902,N805,ANN001,WPS110,ANN201,B950
        """Above noqa ignores are due to below issue.

        https://github.com/pydantic/pydantic/issues/506#issuecomment-1127789412
        """
        if (values.get("outbound") is None) and (values.get("inbound") is None):
            raise ValueError("At least one of 'outbound' or 'inbound' is required")
        return values
