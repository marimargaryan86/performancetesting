from pydantic.v1 import Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.link import Link
from snowfall.vendor.benerail.models.metadata import Metadata
from snowfall.vendor.benerail.models.products.product import Product


class GetProductResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: Product = Field(..., alias="result")
    links: list[Link] | None = None
