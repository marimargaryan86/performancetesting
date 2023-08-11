from pydantic import Field

from snowfall.vendor.benerail.models import etag
from snowfall.vendor.benerail.models import etag as etag_models
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


class GetBookingResponse(BenerailBaseModel):
    metadata: Metadata
    response_result: Booking = Field(..., alias="result")
    links: list[Link] | None = None
    dialogue_etag: str

    @property
    def booking_etag(self) -> str:
        return self.metadata.resource_etag or ""

    def set_etags(self, etag_data: etag_models.EtagData) -> None:
        etag_data.dialogue_etag = self.dialogue_etag
        etag_data.booking_etag = self.booking_etag


class GetOrderResponse(BenerailBaseModel):
    metadata: Metadata
    response_result: Order = Field(..., alias="result")
    links: list[Link] | None = None
    booking_etag: str

    @property
    def order_etag(self) -> str:
        return self.metadata.resource_etag or ""

    def set_etags(self, etag_data: etag_models.EtagData) -> None:
        etag_data.booking_etag = self.booking_etag
        etag_data.order_etag = self.order_etag


class GetSelectedOfferResponse(BenerailBaseModel):
    metadata: Metadata
    response_result: SelectedOffer | None = Field(None, alias="result")
    links: list[Link] | None = None

    order_etag: str

    @property
    def selected_offer_etag(self) -> str:
        return self.metadata.resource_etag or ""

    def set_etags(self, etag_data: etag_models.EtagData) -> None:
        etag_data.order_etag = self.order_etag
        etag_data.selected_offer_etag = self.selected_offer_etag


class GetSelectedOfferPartResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: SelectedOfferPart | None = Field(None, alias="result")
    links: list[Link] | None = None


class GetBookedOfferResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: BookedOffer | None = Field(None, alias="result")
    links: list[Link] | None = None


class GetBookedOfferPartResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: BookedOfferPart | None = Field(None, alias="result")
    links: list[Link] | None = None


class GetBookedTripResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: BookedTrip | None = Field(None, alias="result")
    links: list[Link] | None = None


class GetPaymentResourceResponse(BenerailBaseModel):
    metadata: Metadata
    response_result: Payment = Field(..., alias="result")
    links: list[Link] | None = None
    order_etag: str

    @property
    def payment_etag(self) -> str:
        return self.metadata.resource_etag or ""

    def set_etags(self, etag_data: etag.EtagData) -> None:
        etag_data.payment_etag = self.payment_etag
        etag_data.order_etag = self.order_etag


class GetFulfillmentResponse(BenerailBaseModel):
    metadata: Metadata
    response_result: Fulfillment = Field(..., alias="result")
    links: list[Link] | None = None
    booking_etag: str

    @property
    def fulfillments_etag(self) -> str:
        return self.metadata.resource_etag or ""

    def set_etags(self, etag_data: etag.EtagData) -> None:
        etag_data.booking_etag = self.booking_etag
        etag_data.fulfillments_etag = self.fulfillments_etag


class GetRefundOfferResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: RefundOffer | None = Field(None, alias="result")
    links: list[Link] | None = None
