from pydantic.v1 import Field

from snowfall.vendor.benerail.models import etag
from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.booking import (
    BookedOfferPart,
    BookedTrip,
    Booking,
    Fulfillment,
)
from snowfall.vendor.benerail.models.bookings.offer import (
    BookedOffer,
    RefundOffer,
    SelectedOffer,
    SelectedOfferPart,
)
from snowfall.vendor.benerail.models.bookings.order import Order
from snowfall.vendor.benerail.models.bookings.payment import Payment
from snowfall.vendor.benerail.models.link import Link
from snowfall.vendor.benerail.models.metadata import Metadata


class BaseResponse(BenerailBaseModel):
    metadata: Metadata
    links: list[Link] | None = None

    @property
    def etag(self) -> str:
        return getattr(self.metadata, "resource_etag", "")


class GetBookingResponse(BaseResponse):
    response_result: Booking = Field(..., alias="result")
    dialogue_etag: str

    def set_etags(self, etag_data: etag.EtagData) -> None:
        etag_data.dialogue_etag = self.dialogue_etag
        etag_data.booking_etag = self.etag


class GetOrderResponse(BaseResponse):
    response_result: Order = Field(..., alias="result")
    booking_etag: str

    def set_etags(self, etag_data: etag.EtagData) -> None:
        etag_data.booking_etag = self.booking_etag
        etag_data.order_etag = self.etag


class GetSelectedOfferResponse(BaseResponse):
    response_result: SelectedOffer | None = Field(None, alias="result")
    order_etag: str

    def set_etags(self, etag_data: etag.EtagData) -> None:
        etag_data.order_etag = self.order_etag
        etag_data.selected_offer_etag = self.etag


class GetSelectedOfferPartResponse(BaseResponse):
    response_result: SelectedOfferPart | None = Field(None, alias="result")


class GetBookedOfferResponse(BaseResponse):
    response_result: BookedOffer | None = Field(None, alias="result")


class GetBookedOfferPartResponse(BaseResponse):
    response_result: BookedOfferPart = Field(..., alias="result")


class GetBookedTripResponse(BaseResponse):
    response_result: BookedTrip | None = Field(None, alias="result")


class GetPaymentResourceResponse(BaseResponse):
    response_result: Payment = Field(..., alias="result")
    order_etag: str

    def set_etags(self, etag_data: etag.EtagData) -> None:
        etag_data.payment_etag = self.etag
        etag_data.order_etag = self.order_etag


class GetFulfillmentResponse(BaseResponse):
    response_result: Fulfillment = Field(..., alias="result")
    booking_etag: str

    def set_etags(self, etag_data: etag.EtagData) -> None:
        etag_data.booking_etag = self.booking_etag
        etag_data.fulfillments_etag = self.etag


class GetRefundOfferResponse(BaseResponse):
    response_result: RefundOffer = Field(..., alias="result")
