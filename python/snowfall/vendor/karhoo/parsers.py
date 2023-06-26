import datetime
from typing import Any

from snowfall.vendor.karhoo.models import bookings, location, passenger


def parse_coordinates(
    coordinates: location.Coordinates,
) -> dict[str, Any]:
    return {
        "latitude": coordinates.latitude,
        "longitude": coordinates.longitude,
        "display_address": coordinates.display_address,
    }


def parse_request_quotes_request(
    origin: location.Coordinates,
    destination: location.Coordinates,
    departure_at: datetime.datetime | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "origin": parse_coordinates(origin),
        "destination": parse_coordinates(destination),
    }

    if departure_at:
        payload["local_time_of_pickup"] = departure_at.strftime("%Y-%m-%dT%H:%M")

    return payload


def parse_booking_cancellation(
    reason: str,
    explanation: str | None,
) -> dict[str, Any]:
    return {
        "reason": reason,
        "explanation": explanation,
    }


def parse_passenger_details(
    passenger_details: passenger.PassengerDetails,
) -> dict[str, Any]:
    return {
        "first_name": passenger_details.first_name,
        "last_name": passenger_details.last_name,
        "email": passenger_details.email,
        "phone_number": passenger_details.phone_number,
        "locale": passenger_details.locale,
    }


def parse_luggage(
    luggage: passenger.Luggage,
) -> dict[str, Any]:
    return {
        "total": luggage.total,
    }


def parse_passengers(
    passengers: passenger.Passengers,
) -> dict[str, Any]:
    return {
        "additional_passengers": passengers.additional_passengers,
        "passenger_details": [
            parse_passenger_details(passenger_details)
            for passenger_details in passengers.passenger_details
        ],
        "luggage": parse_luggage(passengers.luggage),
    }


def parse_book_trip(booking: bookings.Booking) -> dict[str, Any]:
    return {
        "meta": booking.meta,
        "quote_id": booking.quote_id,
        "passengers": parse_passengers(booking.passengers),
        "partner_trip_id": booking.partner_trip_id,
        "comments": booking.comments,
        "flight_number": booking.flight_number,
        "train_number": booking.train_number,
        "cost_center_reference": booking.cost_center_reference,
        "train_time": booking.train_time,
    }
