import datetime
import uuid

import pydantic

from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema
from snowfall.vendor.ba_ndc.models.payment_type_schemas import (
    CashPayment,
    CreditCardPayment,
)
from snowfall.vendor.ba_ndc.models.util import offer_enums


class OriginDestination(BaseSchema):
    identifier: str = pydantic.Field(..., alias="id")
    departure_date: datetime.date | None = pydantic.Field(description="Departure date.")


class OrderReshopRequest(BaseSchema):
    cabin_preference: offer_enums.CabinTypeEnum | None = pydantic.Field(
        description="Preferred cabin type.",
    )
    origin_destinations: list[OriginDestination] = pydantic.Field(
        description="OriginDestinations.",
    )


class RepriceRequest(BaseSchema):
    offer_id: uuid.UUID


class AcceptReshopOfferRequest(BaseSchema):
    reshop_offer_id: uuid.UUID | None = pydantic.Field(
        description="Reshop offer ID to accept.",
    )
    reprice_offer_id: uuid.UUID | None = pydantic.Field(
        description="Reprice offer ID to accept.",
    )
    payment: CreditCardPayment | CashPayment | None = pydantic.Field(
        description="Order payment",
        discriminator="payment_type",
    )
