from pydantic import Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.enumeration.rcode import RcoderesultLabels
from snowfall.vendor.benerail.models.types import Latitude, Longitude


class Address(BenerailBaseModel):
    """Address is yet to be implemented by Benerail themselves."""


class PointOfInterest(BenerailBaseModel):
    place_type: str | None = Field(None, description="poi")


class GeoPosition(BenerailBaseModel):
    longitude: Longitude
    latitude: Latitude


class Station(BenerailBaseModel):
    place_type: str | None = Field(None, description="station")
    country: str | None = Field(None, example="FI")
    zone_id: str | None = Field(None, example="Europe/Paris")
    codes: dict[str, str] | None = Field(
        None,
        example={
            "bnds": "urn:bnds:tstatn_id:NLASC",
            "uic": "urn:uic:tstatn_id:118400058",
            "pao": "urn:pao:tstatn_id:NLAMA",
        },
    )
    labels: dict[str, RcoderesultLabels] | None = Field(
        None,
        example={
            "nl/nl": {
                "codeShort": "NLASC",
                "codeLong": "NLASC",
                "text": "Amsterdam Centraal Station",
            },
            "en": {
                "codeShort": "NLASC",
                "codeLong": "NLASC",
                "text": "Amsterdam Centraal Station",
            },
            "*": {
                "codeShort": "NLASC",
                "codeLong": "NLASC",
                "text": "Amsterdam Centraal Station",
            },
        },
    )
