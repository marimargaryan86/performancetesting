from collections.abc import Sequence

import pydantic

from snowfall.vendor.direct_ferries import enums
from snowfall.vendor.direct_ferries.models import base


class TicketType(base.CamelCaseBaseModel):
    identifier: int = pydantic.Field(..., alias="id")
    title: str
    description: str
    total_in_selected_currency: float
    is_amendable: bool
    is_amendment_fee_charged: bool
    is_cancellable: bool
    is_refund_fee_charged: bool
    sales_messages: Sequence[str] | None
    compulsory_accommodation_id: int
    tariff_type: str
    tariff_band: str
    tariff_promotion: str
    tariff_flexibility: str
    tariff_band_description: str
    set_by_ticket_type: bool
    send_tariff_as: enums.SendTariffAs


class TicketTypesResponse(base.CamelCaseBaseModel):
    ticket_type_message: str | None
    ticket_types: Sequence[TicketType]
