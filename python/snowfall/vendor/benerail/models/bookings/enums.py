from enum import Enum


class PreferenceType(Enum):
    required = "REQUIRED"
    unacceptable = "UNACCEPTABLE"


class PaymentStates(Enum):
    initiated = "initiated"
    confirmed = "confirmed"
    succeeded = "succeeded"
    failed = "failed"
    aborted = "aborted"


class BookedOfferStatus(Enum):
    selected = "SELECTED"
    prebooked = "PREBOOKED"
    booked = "BOOKED"


class Optionality(Enum):
    required_res = "REQUIRED_RES"
    optional_res = "OPTIONAL_RES"


class PlacementType(Enum):
    passengers = "passengers"
    bicycles = "bicycles"


class Direction(Enum):
    single_travel = "single-travel"
    outward_travel = "outward-travel"
    return_travel = "return-travel"
    roundtrip_travel = "roundtrip-travel"


class LegType(Enum):
    timed = "TIMED"
    transfer = "TRANSFER"


class BookingErrorCodes(Enum):
    booked_offer_for_order_illegal_state = "booked.offer.for.order.illegal.state"
    booked_offer_not_found = "booked.offer.not.found"
    booked_offer_part_not_found = "booked.offer.part.not.found"
    booked_trip_not_found = "booked.trip.not.found"
    booking_not_found = "booking.not.found"
    dialogue_not_found = "dialogue.not.found"
    dnr_for_booking_not_found = "dnr.for.booking.not.found"
    dossier_already_locked = "dossier.already.locked"
    error_retrieving_dossier = "error.retrieving.dossier"
    dossier_not_found = "dossier.not.found"
    payment_method_not_found = "payment.method.not.found"
    ticket_production_not_found = "ticket.production.not.found"
    error_creating_payment = "error.creating.payment"
    sales_order_not_found = "sales.order.not.found"
    selected_offer_not_found = "selected.offer.not.found"
    selected_offer_part_not_found = "selected.offer.part.not.found"
    inventory_order_not_found = "inventory.order.not.found"
    fulfillment_not_found = "fulfillment.not.found"
    incorrect_status_for_order = "incorrect.status.for.order"
    invalid_dossier = "invalid.dossier"
    order_for_booking_illegal_state = "order.for.booking.illegal.state"
    order_for_booking_not_found = "order.for.booking.not.found"
    order_not_found = "order.not.found"
    booking_option_not_allowed = "booking.option.not.allowed"
    passenger_not_found = "passenger.not.found"
    offer_part_required_in_offer = "offer.part.required.in.offer"


class Severity(Enum):
    error = "error"
    warning = "warning"
