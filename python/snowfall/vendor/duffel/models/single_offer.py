import pydantic

from snowfall.vendor.duffel.models.base import DuffelBaseModel
from snowfall.vendor.duffel.models.offer import Offer


class SingleOfferResponse(DuffelBaseModel):
    response_data: Offer = pydantic.Field(..., alias="data")
