import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.booking import (
    BookedOfferPart,
    BookedTrip,
    Booking,
    Fulfillment,
)
from snowfall.vendor.benerail.models.bookings.offer import (
    BookedOffer,
    SelectedOffer,
    SelectedOfferPart,
)
from snowfall.vendor.benerail.models.bookings.order import Order
from snowfall.vendor.benerail.models.bookings.payment import Payment
from snowfall.vendor.benerail.models.link import Link
from snowfall.vendor.benerail.models.metadata import MetaData


class GetBookingResponse(BenerailBaseModel):
    metadata: MetaData | None
    response_result: Booking | None = pydantic.Field(..., alias="result")
    links: list[Link] | None


class GetOrderResponse(BenerailBaseModel):
    metadata: MetaData | None
    response_result: Order | None = pydantic.Field(..., alias="result")
    links: list[Link] | None


class GetSelectedOfferResponse(BenerailBaseModel):
    metadata: MetaData | None
    response_result: SelectedOffer | None = pydantic.Field(..., alias="result")
    links: list[Link] | None


class GetSelectedOfferPartResponse(BenerailBaseModel):
    metadata: MetaData | None
    response_result: SelectedOfferPart | None = pydantic.Field(..., alias="result")
    links: list[Link] | None


class GetBookedOfferResponse(BenerailBaseModel):
    metadata: MetaData | None
    response_result: BookedOffer | None = pydantic.Field(..., alias="result")
    links: list[Link] | None


class GetBookedOfferPartResponse(BenerailBaseModel):
    metadata: MetaData | None
    response_result: BookedOfferPart | None = pydantic.Field(..., alias="result")
    links: list[Link] | None


class GetBookedTripResponse(BenerailBaseModel):
    metadata: MetaData | None
    response_result: BookedTrip | None = pydantic.Field(..., alias="result")
    links: list[Link] | None


class GetPaymentResourceResponse(BenerailBaseModel):
    metadata: MetaData | None
    response_result: Payment | None = pydantic.Field(..., alias="result")
    links: list[Link] | None


class GetFulfillmentResponse(BenerailBaseModel):
    metadata: MetaData | None
    response_result: Fulfillment | None = pydantic.Field(..., alias="result")
    links: list[Link] | None
