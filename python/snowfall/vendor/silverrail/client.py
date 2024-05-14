import dataclasses
from typing import Any, TypeVar

import httpx
from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.serializers import XmlSerializer

from snowfall.stdlib.transport.http import client
from snowfall.vendor.silverrail import errors
from snowfall.vendor.silverrail.models import booking, stations
from snowfall.vendor.silverrail.models.shopping import (
    ContextType,
    PointToPointShoppingQuery,
    PointToPointShoppingRequest,
    PointToPointShoppingResponse,
    ShoppingPointToPointShopInput,
    ShoppingPointToPointShopOutput,
)

T = TypeVar("T")  # noqa: WPS111

SHOPPING_SERVICE_PATH = "/shopping-ws/services/Shopping/v2"
BOOKING_SERVICE_PATH = "/booking-ws/services/Booking/v2"
PUBLISHED_DATA_API_PATH = "/pub-ws"


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
        self._shopping_context = ContextType(
            distributor_code=settings.distributor_code,
            point_of_sale_code=settings.pos_code,
            channel_code=settings.channel_code,
        )
        self._booking_context = booking.ContextType(
            distributor_code=settings.distributor_code,
            point_of_sale_code=settings.pos_code,
            channel_code=settings.channel_code,
        )

    async def create_booking_record(
        self,
        passengers: booking.CreateBookingRecordRequestType.Passengers,
        leg_solution: booking.LegSolutionsType,
        prices: booking.CreateBookingRecordRequestType.Prices,
    ) -> booking.CreateBookingRecordResponse:
        request = booking.BookingCreateBookingRecordInput(
            body=booking.BookingCreateBookingRecordInput.Body(
                create_booking_record_request=booking.CreateBookingRecordRequest(
                    response_spec=booking.CreateBookingRecordRequestType.ResponseSpec(
                        return_reservation_details=True,
                    ),
                    context=self._booking_context,
                    passengers=passengers,
                    leg_solutions=leg_solution,
                    prices=prices,
                ),
            ),
        )

        output = await self._make_soap_request(
            request=request,
            api_path=BOOKING_SERVICE_PATH,
            result_class=booking.BookingCreateBookingRecordOutput,
        )

        if output.body is None:
            raise errors.SilverrailUnexpectedFormatError()
        if output.body.create_booking_record_response is None:
            raise errors.SilverrailUnexpectedFormatError()

        return output.body.create_booking_record_response

    async def shopping_point_to_point(
        self,
        query: PointToPointShoppingQuery,
    ) -> PointToPointShoppingResponse:
        req = ShoppingPointToPointShopInput(
            body=ShoppingPointToPointShopInput.Body(
                point_to_point_shopping_request=PointToPointShoppingRequest(
                    context=self._shopping_context,
                    point_to_point_shopping_query=query,
                ),
            ),
        )

        output = await self._make_soap_request(
            request=req,
            api_path=SHOPPING_SERVICE_PATH,
            result_class=ShoppingPointToPointShopOutput,
        )

        if output.body is None:
            raise errors.SilverrailUnexpectedFormatError()
        if output.body.point_to_point_shopping_response is None:
            raise errors.SilverrailUnexpectedFormatError()

        return output.body.point_to_point_shopping_response

    async def get_stations(self) -> list[stations.StationType]:
        req = stations.PublishingAPIInput(
            body=stations.PublishingAPIInput.Body(
                request=stations.DataRequestType(
                    type_value=stations.SrtDataType.STATION,
                ),
            ),
        )

        output = await self._make_soap_request(
            request=req,
            api_path=PUBLISHED_DATA_API_PATH,
            result_class=stations.PublishingAPIOutput,
        )

        if output.body is None or output.body.data_response is None:
            raise errors.SilverrailUnexpectedFormatError()
        if output.body.data_response.request_status is None:
            raise errors.SilverrailUnexpectedFormatError()
        if not output.body.data_response.request_status.success:
            raise errors.RequestFailedError()
        return output.body.data_response.stations

    async def get_acceptable_fop(self) -> list[stations.AcceptableFopType]:
        request = stations.PublishingAPIInput(
            body=stations.PublishingAPIInput.Body(
                request=stations.DataRequestType(
                    type_value=stations.SrtDataType.ACCEPTABLE_FOP,
                ),
            ),
        )

        output = await self._make_soap_request(
            request=request,
            api_path=PUBLISHED_DATA_API_PATH,
            result_class=stations.PublishingAPIAcceptableFOPOutput,
        )

        if output.body is None or output.body.data_response is None:
            raise errors.SilverrailUnexpectedFormatError()
        if output.body.data_response.request_status is None:
            raise errors.SilverrailUnexpectedFormatError()
        if not output.body.data_response.request_status.success:
            raise errors.RequestFailedError()
        return output.body.data_response.acceptable_fop

    async def get_booking_record(
        self,
        record_locator: str,
    ) -> booking.RetrieveBookingRecordResponse:
        request = booking.BookingRetrieveBookingRecordRequestInput(
            body=booking.BookingRetrieveBookingRecordRequestInput.Body(
                retrieve_booking_record_request=booking.RetrieveBookingRecordRequest(
                    response_spec=booking.RetrieveBookingRecordRequestType.ResponseSpec(
                        include_financials=True,
                    ),
                    record_locator=record_locator,
                    context=self._booking_context,
                ),
            ),
        )
        output = await self._make_soap_request(
            request=request,
            api_path=BOOKING_SERVICE_PATH,
            result_class=booking.BookingRetrieveBookingRecordRequestOutput,
        )

        if output.body is None or output.body.retrieve_booking_record_response is None:
            raise errors.SilverrailUnexpectedFormatError()

        return output.body.retrieve_booking_record_response

    async def add_payment(
        self,
        record_locator: str,
        payment: booking.AbstractPaymentRequestType.Payment,
    ) -> booking.AddPaymentResponse:
        request = booking.BookingAddPaymentRequestInput(
            body=booking.BookingAddPaymentRequestInput.Body(
                add_payment_request=booking.AddPaymentRequest(
                    context=self._booking_context,
                    record_locator=record_locator,
                    payment=payment,
                    fulfillment_information=booking.FulfillmentInformationType(
                        ticket_option=booking.TicketingOptionType(
                            code=booking.TicketingOptionTypeCode.EML,
                            type_value="E_MAIL",
                            destination="Ticket by E-mail",
                        ),
                    ),
                ),
            ),
        )
        output = await self._make_soap_request(
            request=request,
            api_path=BOOKING_SERVICE_PATH,
            result_class=booking.BookingAddPaymentRequestOutput,
        )

        if output.body is None or output.body.add_payment_response is None:
            raise errors.SilverrailUnexpectedFormatError()

        return output.body.add_payment_response

    async def confirm_booking(
        self,
        record_locator: str,
    ) -> booking.ConfirmBookingRecordResponse:
        request = booking.BookingConfirmBookingRecordRequestInput(
            body=booking.BookingConfirmBookingRecordRequestInput.Body(
                confirm_booking_record_request=booking.ConfirmBookingRecordRequest(
                    context=self._booking_context,
                    record_locator=record_locator,
                ),
            ),
        )
        output = await self._make_soap_request(
            request=request,
            api_path=BOOKING_SERVICE_PATH,
            result_class=booking.BookingConfirmBookingRecordRequestOutput,
        )

        if output.body is None or output.body.confirm_booking_record_response is None:
            raise errors.SilverrailUnexpectedFormatError()

        return output.body.confirm_booking_record_response

    async def _make_soap_request(
        self,
        request: Any,
        api_path: str,
        result_class: type[T],
    ) -> T:
        serializer = XmlSerializer()
        soap_request_body = serializer.render(request)
        response = await self._make_raw_soap_request(
            soap_request_body=soap_request_body,
            path=api_path,
        )

        parser = XmlParser()
        return parser.from_string(
            response.text,
            result_class,
        )

    async def _make_raw_soap_request(
        self,
        soap_request_body: str,
        path: str,
        timeout: httpx.Timeout | int | None = None,
    ) -> httpx.Response:
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
        }

        return await self._make_request(
            options=client.RequestOptions(
                method="POST",
                path=path,
                headers=headers,
                raw_content=soap_request_body,
            ),
            timeout=timeout,
        )
