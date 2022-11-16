from typing import Optional

import pydantic

from snowfall.vendor.distribusion.models.base import DistribusionBaseModel


class MarketingCarrier(DistribusionBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    code: str
    trade_name: str


class MarketingCarrierDetails(DistribusionBaseModel):
    code: str
    trade_name: str
    legal_name: str
    address: str
    phone: str
    fax: str
    customer_service_phone: str
    customer_service_email: str
    email: str
    commercial_register: str
    commercial_register_number: str
    vat_no: str
    authorised_representative: str
    white_label_logo: str
    white_label_colour_code: str
    terms: str
    privacy_policy: Optional[str]
    flight_number_required: bool
    has_mobile_tickets: bool
    tickets_validity_in_hours: Optional[str]
    tickets_validity_info: str
    cancellation_type: str
    status: str
    supports_seats: bool
    ticket_printing_required: bool
    booking_fee: int
    cancellation_fee: int
    cancellation_cutoff: int
