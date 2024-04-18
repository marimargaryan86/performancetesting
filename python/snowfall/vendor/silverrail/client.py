import dataclasses

import httpx
from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.serializers import XmlSerializer

from snowfall.stdlib.transport.http import client
from snowfall.vendor.silverrail.models.shopping import (
    ContextType,
    PointToPointShoppingQuery,
    PointToPointShoppingRequest,
    PointToPointShoppingResponse,
    ShoppingPointToPointShopInput,
    ShoppingPointToPointShopOutput,
)

SHOPPING_SERVICE_PATH = "/shopping-ws/services/Shopping/v2"


class SilverrailUnexpectedFormatError(Exception):
    """Raised when the message retunred by Silverrail had an unexpected format."""


# The settings for the client (customer) of the API. This will limit
# the access to providers depending on which business agreements the
# client has with Silverrail. For us this will be some Snowfall-specific
# settings, which will depend on which channel we search in.
@dataclasses.dataclass(frozen=True)
class SilverrailSettings:
    distributor_code: str
    pos_code: str
    channel_code: str


class SilverrailClient(client.HttpClient):
    def __init__(
        self,
        base_url: str,
        settings: SilverrailSettings,
        http_client: httpx.AsyncClient,
    ):
        super().__init__(base_url, http_client)
        self._context = ContextType(
            distributor_code=settings.distributor_code,
            point_of_sale_code=settings.pos_code,
            channel_code=settings.channel_code,
        )

    async def shopping_point_to_point(
        self,
        query: PointToPointShoppingQuery,
    ) -> PointToPointShoppingResponse:
        req = ShoppingPointToPointShopInput(
            body=ShoppingPointToPointShopInput.Body(
                point_to_point_shopping_request=PointToPointShoppingRequest(
                    context=self._context,
                    point_to_point_shopping_query=query,
                ),
            ),
        )
        serializer = XmlSerializer()
        soap_request_body = serializer.render(req)
        response = await self._make_soap_request(soap_request_body)

        parser = XmlParser()
        output: ShoppingPointToPointShopOutput = parser.from_string(
            response.text,
            ShoppingPointToPointShopOutput,
        )

        if output.body is None:
            raise SilverrailUnexpectedFormatError()
        if output.body.point_to_point_shopping_response is None:
            raise SilverrailUnexpectedFormatError()

        return output.body.point_to_point_shopping_response

    async def _make_soap_request(
        self,
        soap_request_body: str,
        timeout: httpx.Timeout | int | None = None,
    ) -> httpx.Response:
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
        }

        return await self._make_request(
            options=client.RequestOptions(
                method="POST",
                path=SHOPPING_SERVICE_PATH,
                headers=headers,
                raw_content=soap_request_body,
            ),
            timeout=timeout,
        )
