import enum


class Gender(enum.Enum):
    male = "M"
    female = "F"
    other = "X"


class DialogueErrorCodes(enum.Enum):
    booking_already_exists = "booking.already.exists"
    changing_dob_not_allowed = "changing.dob.not.allowed"
    dialogue_not_found = "dialogue.not.found"
    external_id_not_found_in_dialogue = "external.id.not.found.in.dialogue"
    incorrect_status_for_journey = "incorrect.status.for.journey"
    internal_id_not_found_in_dialogue = "internal.id.not.found.in.dialogue"
    invalid_dossier = "invalid.dossier"
    invalid_timestamp = "invalid.timestamp"
    no_timezone_in_timestamp = "no.timezone.in.timestamp"
    inward_date_outward_offer = "inward.date.outward.offer"
    unknown_gender = "unknown.gender"
    passenger_corporate_contract_invalid = "passenger.corporate.contract.invalid"
    passenger_corporate_contract_fce_required = (
        "passenger.corporate.contract.fce.required "
    )
    passenger_invalid = "passenger.invalid"
    passenger_not_found = "passenger.not.found"
    passenger_required_for_trip_offer_filter = (
        "passenger.required.for.trip.offer.filter"
    )
    passenger_unknown_card = "passenger.unknown.card"
    passenger_loyalty_card_no_number = "passenger.loyalty.card.no.number"
    booker_invalid = "booker.invalid"
    booker_not_found = "booker.not.found"
    booker_email_to_required = "booker.email.to.required"
    booker_on_ticket_invalid = "booker.on.ticket.invalid"
    booker_delete_not_allowed = "booker.delete.not.allowed"
    booker_create_not_allowed = "booker.create.not.allowed"
    invalid_urn = "invalid.urn"
    trip_filter_not_found_for_dialogue = "trip.filter.not.found.for.dialogue"
    trip_offer_filter_not_found_for_dialogue = (
        "trip.offer.filter.not.found.for.dialogue"
    )
    unknown_id_type = "unknown.id.type"
    wrong_state = "wrong.state"
    xref_not_found_in_dialogue = "xref.not.found.in.dialogue"


class BookingErrorCodes(enum.Enum):
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


class PricingCalendarErrorCodes(enum.Enum):
    destination_not_found = "destination.not.found"
    invalid_date_format = "invalid.date.format"
    origin_not_found = "origin.not.found"
    period_invalid = "period.invalid"


class ProductErrorCodes(enum.Enum):
    cannot_serialize_provisional_order_to_json = (
        "cannot.serialize.provisional.order.to.json"
    )
    product_not_found = "product.not.found"


class TripErrorCodes(enum.Enum):
    trip_not_found = "trip.not.found"
    trip_collection_not_found = "trip.collection.not.found"
    origin_not_found = "origin.not.found"
    destination_not_found = "destination.not.found"
    train_type_not_found = "train.type.not.found"


class OrderStates(enum.Enum):
    created = "created"
    info_required = "info_required"
    bookable = "bookable"
    provisional = "provisional"
    payment_pending = "payment_pending"
    confirmed = "confirmed"
    aborted = "aborted"
    order_error = "error"


class ServiceClassType(enum.Enum):
    best = "BEST"
    high = "HIGH"
    standard = "STANDARD"
    basic = "BASIC"


class PaymentStates(enum.Enum):
    initiated = "initiated"
    confirmed = "confirmed"
    succeeded = "succeeded"
    failed = "failed"
    aborted = "aborted"
