import datetime

from snowfall.stdlib.transport.http import client
from snowfall.vendor.benerail.clients import base
from snowfall.vendor.benerail.models.products import response as product_response

_BASE_PATH = "/products"


class ProductsClient(base.BenerailBaseClient):
    async def get_product_info(
        self,
        product_id: str,
        sales_date: datetime.date,
        travel_date: datetime.date,
    ) -> product_response.GetProductResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="{prefix}/products/{product_id}".format(
                    prefix=_BASE_PATH,
                    product_id=product_id,
                ),
                query={
                    "sales-date": str(sales_date),
                    "travel-date": str(travel_date),
                },
                headers=self._get_headers(),
            ),
        )

        return product_response.GetProductResponse(**response.json())
