from typing import Optional, Sequence

from pydantic import BaseModel


class VendorStation(BaseModel):
    uid: str
    name: str
    location: Optional[str]
    searchable: bool


class VendorStationsResponse(BaseModel):
    stations: Sequence[VendorStation]
