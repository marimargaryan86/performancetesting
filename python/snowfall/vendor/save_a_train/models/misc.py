from collections.abc import Sequence

from pydantic import BaseModel


class VendorStation(BaseModel):
    uid: str
    name: str
    location: str | None
    searchable: bool


class VendorStationsResponse(BaseModel):
    stations: Sequence[VendorStation]
