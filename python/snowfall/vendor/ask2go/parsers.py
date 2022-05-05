import datetime
from typing import Any, Union

from snowfall.vendor.ask2go.models import common, search


def parse_search_criteria(
    origin_iata: str,
    destination_iata: str,
    date: Union[datetime.date, datetime.datetime],
) -> dict[str, Any]:
    return {
        "origin": origin_iata,
        "destination": destination_iata,
        "departure": date.isoformat(),
    }


def parse_search_request(criteria: search.CreateSearchCriteria) -> dict[str, Any]:
    search_criteria = [
        parse_search_criteria(
            criteria.origin_iata,
            criteria.destination_iata,
            criteria.outbound_date,
        ),
    ]

    if criteria.inbound_date:
        direction = "Both"

        search_criteria.append(
            parse_search_criteria(
                criteria.destination_iata,
                criteria.origin_iata,
                criteria.inbound_date,
            ),
        )
    else:
        direction = "Outbound"

    return {
        "adults": criteria.adults,
        "children": criteria.children,
        "infants": criteria.infants,
        "cabinClass": criteria.cabin_class.value,
        "direction": direction,
        "searchCriteria": search_criteria,
    }


def parse_create_booking_request(
    pricing_id: str,
    transaction_id: str,
    passenger: common.Passenger,
    contact: common.Contact,
) -> dict[str, Any]:
    return {
        "pricingId": pricing_id,
        "transactionId": transaction_id,
        "contactDetails": {
            "firstName": passenger.first_name,
            "lastName": passenger.last_name,
            "title": passenger.name_title,
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
                "dateOfBirth": passenger.birth_date.isoformat(),
                "gender": passenger.gender.value,
                "passengerType": passenger.type.value,
            },
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
