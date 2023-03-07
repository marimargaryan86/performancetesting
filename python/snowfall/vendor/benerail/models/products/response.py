import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.link import Link
from snowfall.vendor.benerail.models.metadata import MetaData
from snowfall.vendor.benerail.models.products.product import Product


class GetProductResponse(BenerailBaseModel):
    metadata: MetaData | None
    response_result: Product | None = pydantic.Field(..., alias="result")
    links: list[Link] | None
