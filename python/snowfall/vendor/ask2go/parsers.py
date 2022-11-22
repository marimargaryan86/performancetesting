import datetime
from typing import Any, Optional, Sequence

import more_itertools

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

    return request_body


def _parse_traveler_document(
    traveler_document: Optional[common.TravelerDocument],
) -> dict[str, Any]:
    return (
        {
            "nationality": traveler_document.nationality,
            "travellerDocument": {
                "documentType": traveler_document.document_type.value,
                "documentNumber": traveler_document.document_number,
                "documentIssueCountry": traveler_document.document_issue_country,
                "documentExpirationDate": traveler_document.document_exp_date.isoformat(),
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
            "firstName": first_passenger.first_name,
            "lastName": first_passenger.last_name,
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
                "firstName": passenger.first_name,
                "lastName": passenger.last_name,
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
    }


def parse_validated_offer_criteria(
    criteria: validate_offer_criteria.ValidateOfferCriteria,
) -> dict[str, Any]:
    return {
        "transactionId": criteria.transaction_id,
        "clientIp": criteria.client_ip,
        "currency": criteria.currency,
        "flightSegments": [
            {
                "tripNumber": segment.trip_number,
                "segmentNumber": segment.segment_number,
                "flightNumber": segment.flight_number,
                "departureDate": segment.departure_date.isoformat(),
                "arrivalDate": segment.arrival_date.isoformat(),
                "origin": segment.origin_iata,
                "destination": segment.destination_iata,
                "marketingAirline": segment.marketing_airline,
                "operatingAirline": segment.operating_airline,
                "equipment": segment.equipment,
                "resBookDesigCode": segment.res_book_desig_code,
            }
            for segment in criteria.flight_segments
        ],
        "passengers": [
            {"code": passenger.code.value, "count": passenger.count}
            for passenger in criteria.passengers
        ],
        "ancillaries": [
            {"code": ancillary.code, "numberOfItems": ancillary.number_of_items}
            for ancillary in criteria.ancillaries
        ]
        if criteria.ancillaries
        else None,
    }
