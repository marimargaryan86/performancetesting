from enum import Enum


class OrderStates(Enum):
    created = "created"
    info_required = "info_required"
    bookable = "bookable"
    prebooked = "prebooked"
    prerefunded = "prerefunded"
    refunded_settlement_pending = "refunded_settlement_pending"
    provisional = "provisional"
    payment_pending = "payment_pending"
    confirmed = "confirmed"
    aborted = "aborted"
    order_error = "error"
    ticketed = "ticketed"
    cancelled = "cancelled"


class ServiceClassType(Enum):
    best = "BEST"
    high = "HIGH"
    standard = "STANDARD"
    basic = "BASIC"


class SaleType(Enum):
    exchange_conditions = "EXCHANGE_CONDITIONS"
    provider_information = "PROVIDER_INFORMATION"
    refund_conditions = "REFUND_CONDITIONS"
    ticket_information = "TICKET_INFORMATION"
    travel_conditions = "TRAVEL_CONDITIONS"
    special_information = "SPECIAL_INFORMATION"


class ProductErrorCodes(Enum):
    cannot_serialize_provisional_order_to_json = (
        "cannot.serialize.provisional.order.to.json"
    )
    product_not_found = "product.not.found"


class AfterSalesConditionHorizon(Enum):
    always = "Always"
    never = "Never"
    before_departure = "Before Departure"
