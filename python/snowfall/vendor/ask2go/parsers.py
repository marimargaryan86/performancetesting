import datetime
from collections.abc import Sequence
from typing import Any

import more_itertools
import unidecode

from snowfall.vendor.ask2go.models import common, search, validate_offer_criteria


def parse_search_criteria(
    origin_iata: str,
    destination_iata: str,
    date: datetime.date | datetime.datetime,
    departure_window: tuple[datetime.time, datetime.time] | None = None,
) -> dict[str, Any]:
    search_criteria: dict[str, Any] = {
        "origin": origin_iata,
        "destination": destination_iata,
        "departure": date.isoformat(),
    }

    if departure_window:
        search_criteria["departureWindow"] = {
            "earliest": departure_window[0].isoformat(timespec="minutes"),
            "latest": departure_window[1].isoformat(timespec="minutes"),
        }

    return search_criteria


def parse_search_request(criteria: search.CreateSearchCriteria) -> dict[str, Any]:
    search_criteria = [
        parse_search_criteria(
            criteria.origin_iata,
            criteria.destination_iata,
            criteria.outbound_date,
            criteria.outbound_departure_window,
        ),
    ]

    if criteria.inbound_date:
        direction = "Both"

        search_criteria.append(
            parse_search_criteria(
                criteria.destination_iata,
                criteria.origin_iata,
                criteria.inbound_date,
                criteria.inbound_departure_window,
            ),
        )
    else:
        direction = "Outbound"

    request_body = {
        "adults": criteria.adults,
        "children": criteria.children,
        "infants": criteria.infants,
        "cabinClass": criteria.cabin_class.value,
        "direction": direction,
        "searchCriteria": search_criteria,
    }

    if criteria.transaction_id:
        request_body["transactionId"] = str(criteria.transaction_id)

    if criteria.affiliate_id:
        request_body["affiliateId"] = criteria.affiliate_id

    return request_body


def _parse_traveler_document(
    traveler_document: common.TravelerDocument | None,
) -> dict[str, Any]:
    return (
        {
            "nationality": traveler_document.nationality,
            "travellerDocument": {
                "documentType": traveler_document.document_type.value,
                "documentNumber": traveler_document.document_number,
                "documentIssueCountry": traveler_document.document_issue_country,
                "documentExpirationDate": (
                    traveler_document.document_exp_date.isoformat()
                ),
            },
        }
        if traveler_document
        else {}
    )


def parse_create_booking_request(
    pricing_id: str,
    transaction_id: str,
    passengers: Sequence[common.Passenger],
    contact: common.Contact,
) -> dict[str, Any]:
    first_passenger = more_itertools.first(passengers)
    return {
        "pricingId": pricing_id,
        "transactionId": transaction_id,
        "contactDetails": {
            "firstName": unidecode.unidecode(first_passenger.first_name),
            "lastName": unidecode.unidecode(first_passenger.last_name),
            "title": first_passenger.name_title,
            "address": {
                "street": contact.address,
                "city": contact.city,
                "postalCode": contact.postal_code,
                "countryCode": contact.country.code,
            },
            "phoneInternationalCode": contact.phone.country_code,
            "mobilePhone": contact.phone.number,
            "email": contact.email,
        },
        "travelerDetails": [
            {
                "travelerId": 0,
                "firstName": unidecode.unidecode(passenger.first_name),
                "lastName": unidecode.unidecode(passenger.last_name),
                "title": passenger.name_title,
                "dateOfBirth": passenger.birth_date.strftime("%d-%m-%Y"),
                "gender": passenger.gender.value,
                "passengerType": passenger.type.value,
                **_parse_traveler_document(passenger.traveler_document),
            }
            for passenger in passengers
        ],
        "isPriceChangeAccepted": False,
        "isScheduleChangeAccepted": False,
    }


def parse_update_booking_request(
    booking_ref_id: str,
    transaction_id: str,
    *,
    override_double_booking_check: bool,
) -> dict[str, Any]:
    return {
        "id": booking_ref_id,
        "transactionId": transaction_id,
        "billingDetails": {
            "invoice": {
                "companyName": "",
                "vatNo": "",
                "companyStreetAddress": "",
                "companyCityAddress": "",
                "companyCountry": "",
                "companyPostCode": "",
                "companyEmail": "",
            },
        },
        "isInvoiceRequested": True,
        "overrideDoubleBookingCheck": override_double_booking_check,
    }


def parse_validated_offer_criteria(
    criteria: validate_offer_criteria.ValidateOfferCriteria,
) -> dict[str, Any]:
    return {
        "searchId": criteria.search_id,
        "itineraryId": criteria.itinerary_id,
        "transactionId": criteria.transaction_id,
        "clientIp": criteria.client_ip,
        "currency": criteria.currency,
        "ancillaries": (
            [
                {"code": ancillary.code, "numberOfItems": ancillary.number_of_items}
                for ancillary in criteria.ancillaries
            ]
            if criteria.ancillaries
            else None
        ),
    }
