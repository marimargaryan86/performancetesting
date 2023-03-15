from enum import Enum


class OrderStates(Enum):
    created = "created"
    info_required = "info_required"
    bookable = "bookable"
    provisional = "provisional"
    payment_pending = "payment_pending"
    confirmed = "confirmed"
    aborted = "aborted"
    order_error = "error"


class ServiceClassType(Enum):
    best = "BEST"
    high = "HIGH"
    standard = "STANDARD"
    basic = "BASIC"


class SaleType(Enum):
    sale = "SALE"
    exchange = "EXCHANGE"
    refund = "REFUND"
    travel = "TRAVEL"


class ProductErrorCodes(Enum):
    cannot_serialize_provisional_order_to_json = (
        "cannot.serialize.provisional.order.to.json"
    )
    product_not_found = "product.not.found"
