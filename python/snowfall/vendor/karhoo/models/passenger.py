from snowfall.vendor.karhoo.models.base import KarhooBaseModel


class Luggage(KarhooBaseModel):
    total: int


class PassengerDetails(KarhooBaseModel):
    first_name: str | None
    last_name: str
    email: str | None
    phone_number: str
    locale: str | None


class Passengers(KarhooBaseModel):
    additional_passengers: int | None
    passenger_details: list[PassengerDetails]
    luggage: Luggage
