from enum import Enum


class Gender(Enum):
    male = "M"
    female = "F"
    other = "X"


class DialogueErrorCodes(Enum):
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


class PassengerStatus(Enum):
    created = "created"
    in_use = "in use"
    immutable = "immutable"


class OnTicket(Enum):
    customer_name = "customerName"
    customer_number = "customerNumber"
    topo = "topo"
    none = "none"
