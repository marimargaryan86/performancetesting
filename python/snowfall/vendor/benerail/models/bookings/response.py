from pydantic import Field

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
    metadata: Metadata | None = None
    response_result: Booking | None = Field(None, alias="result")
    links: list[Link] | None = None


class GetOrderResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: Order | None = Field(None, alias="result")
    links: list[Link] | None = None


class GetSelectedOfferResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: SelectedOffer | None = Field(None, alias="result")
    links: list[Link] | None = None


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
    metadata: Metadata | None = None
    response_result: Payment | None = Field(None, alias="result")
    links: list[Link] | None = None


class GetFulfillmentResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: Fulfillment | None = Field(None, alias="result")
    links: list[Link] | None = None


class GetRefundOfferResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: RefundOffer | None = Field(None, alias="result")
    links: list[Link] | None = None
