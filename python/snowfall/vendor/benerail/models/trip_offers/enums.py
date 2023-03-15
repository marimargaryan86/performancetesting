from enum import Enum


class RequestedOfferParts(Enum):
    admission_and_reservation = "admission-and-reservation"
    reservation_only = "reservation-only"
    admission_only = "admission-only"


class TripOffersErrorCodes(Enum):
    cannot_serialize_provisional_order_to_json = (
        "cannot.serialize.provisional.order.to.json"
    )
    product_not_found = "product.not.found"
