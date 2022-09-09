from typing import Optional, Sequence

import pydantic

from snowfall.vendor.direct_ferries.models import base, common


class ImportantInformationItem(base.CamelCaseBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    title: str
    message: str
    info_link: str


class ImportantInformation(base.CamelCaseBaseModel):
    information_items: Sequence[ImportantInformationItem] = pydantic.Field(
        ...,
        alias="items",
    )


class BookingResponse(base.CamelCaseBaseModel):
    operator_ref: str
    barcode_url: str
    booking: common.Booking
    important_information: ImportantInformation


class CancellationEnquiryInformation(base.CamelCaseBaseModel):
    fee: str
    refund_amount: str
    message: Optional[str]
    booking_token: Optional[str]


class CancellationStatus(base.CamelCaseBaseModel):
    identifier: int = pydantic.Field(..., alias="id")
    name: Optional[str]


class CancellationResponse(base.CamelCaseBaseModel):
    cancellation_status: CancellationStatus
    fee: str
    refund_amount: str
    error_message: Optional[str]
    success_message: Optional[str]
