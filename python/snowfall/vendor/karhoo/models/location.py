from snowfall.vendor.karhoo.models.base import KarhooBaseModel


class Coordinates(KarhooBaseModel):
    latitude: float
    longitude: float
    display_address: str | None = None
