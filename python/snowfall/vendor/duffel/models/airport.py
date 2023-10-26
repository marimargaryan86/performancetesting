from snowfall.vendor.duffel.models.base import DuffelListRequest


class AirportListRequest(DuffelListRequest):
    iata_country_code: str | None = None
