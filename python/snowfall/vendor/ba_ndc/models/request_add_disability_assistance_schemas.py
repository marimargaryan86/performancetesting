import pydantic

from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema
from snowfall.vendor.ba_ndc.models.payment_type_schemas import (
    CashPayment,
    CreditCardPayment,
    VoucherPayment,
)


class ServicePassengerPair(BaseSchema):
    service_id: str = pydantic.Field(description="Service ID")
    passenger_id: str = pydantic.Field(description="Passenger ID")


class AddAncillaries(BaseSchema):
    pairs: list[ServicePassengerPair] = pydantic.Field(
        description="Passenger-Service pair",
    )
    payment: CreditCardPayment | CashPayment | VoucherPayment | None = pydantic.Field(
        description="Payment",
        discriminator="type",
    )
