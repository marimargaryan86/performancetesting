import pydantic

from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema
from snowfall.vendor.ba_ndc.models.payment_type_schemas import (
    CashPayment,
    CreditCardPayment,
    VoucherPayment,
)


class SeatPassengerPair(BaseSchema):
    seat_id: str = pydantic.Field(description="Seat ID")
    passenger_id: str = pydantic.Field(description="Passenger ID")


class AddSeats(BaseSchema):
    pairs: list[SeatPassengerPair] = pydantic.Field(description="Passenger-Seat pair")
    payment: CreditCardPayment | CashPayment | VoucherPayment | None = pydantic.Field(
        description="Payment",
        discriminator="payment_type",
    )
