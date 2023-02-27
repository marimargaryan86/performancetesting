import pytest
import pytest_httpx

from snowfall.stdlib.transport.http import errors
from snowfall.vendor.karhoo import client
from snowfall.vendor.karhoo.models import bookings, location, passenger


async def test_request_quotes(
    httpx_mock: pytest_httpx.HTTPXMock,
    karhoo_client: client.KarhooClient,
) -> None:
    httpx_mock.add_response(
        url="https://test_url/v2/quotes",
        status_code=201,
        json={
            "id": "00000000-0000-0000-0000-000000000000",
            "availability": {},
            "quotes": [],
            "status": "PROGRESSING",
        },
    )

    quotes = await karhoo_client.request_quotes(
        origin=location.Coordinates(
            latitude="51.5054564",
            longitude="-0.0775452",
            display_address=None,
        ),
        destination=location.Coordinates(
            latitude="51.501364",
            longitude="-0.14189",
            display_address=None,
        ),
        departure_at=None,
    )

    assert quotes.id == "00000000-0000-0000-0000-000000000000"


async def test_list_quotes(
    httpx_mock: pytest_httpx.HTTPXMock,
    karhoo_client: client.KarhooClient,
) -> None:
    httpx_mock.add_response(
        url="https://test_url/v2/quotes/00000000-0000-0000-0000-000000000000",
        status_code=200,
        json={
            "id": "00000000-0000-0000-0000-000000000000",
            "availability": {},
            "quotes": [],
            "status": "PROGRESSING",
        },
    )

    quotes = await karhoo_client.list_quotes(
        "00000000-0000-0000-0000-000000000000",
    )

    assert quotes.id == "00000000-0000-0000-0000-000000000000"


async def test_list_quotes_not_found(
    httpx_mock: pytest_httpx.HTTPXMock,
    karhoo_client: client.KarhooClient,
) -> None:
    httpx_mock.add_response(
        url="https://test_url/v2/quotes/00000000-0000-0000-0000-000000000000",
        status_code=404,
        json={
            "code": "K3003",
            "message": "Could not get estimates, could not find specified quote,",
        },
    )

    with pytest.raises(errors.HttpStatusError) as exc:
        await karhoo_client.list_quotes(
            "00000000-0000-0000-0000-000000000000",
        )

    assert (
        exc.value.body["message"]  # noqa: WPS441
        == "Could not get estimates, could not find specified quote,"
    )


async def test_book_trip(
    httpx_mock: pytest_httpx.HTTPXMock,
    karhoo_client: client.KarhooClient,
) -> None:
    httpx_mock.add_response(
        url="https://test_url/v1/bookings",
        status_code=201,
        json={
            "id": "00000000-0000-0000-0000-000000000000",
            "passengers": {
                "additional_passengers": 0,
                "passenger_details": [
                    {
                        "first_name": "John",
                        "last_name": "Smith",
                        "email": "john.smith@karhoo.com",
                        "phone_number": "+4412345678",
                        "locale": "en_GB",
                    },
                ],
                "luggage": {"total": 0},
            },
            "traveller_id": "",
            "status": "CONFIRMED",
            "state_details": "",
            "origin": {
                "display_address": "Gatwick Airport (LGW), South Terminal, London, UK",
                "position": {"latitude": 51.157753, "longitude": -0.1619743},
                "place_id": "k_e4fd1bd3-7890-11e9-a982-0a580a040cc9",
                "poi_type": "ENRICHED",
                "timezone": "london/europe",
            },
            "destination": {
                "display_address": (
                    "Buckingham Palace, Westminster, London SW1A 1AA, UK"
                ),
                "position": {"latitude": 51.5086692, "longitude": -0.1375291},
                "place_id": "EhpCcm93bmVsbCBTdCwgU2hlZmZpZWxkLCBVSw",
                "poi_type": "NOT_SET_POI_TYPE",
                "timezone": "london/europe",
            },
            "date_scheduled": "2020-02-17T15:26:59Z",
            "quote": {
                "type": "FIXED",
                "total": 3550,
                "currency": "GBP",
                "gratuity_percent": 0,
                "breakdown": [],
                "vehicle_class": "Saloon",
                "qta_high_minutes": 3,
                "qta_low_minutes": 3,
                "vehicle_attributes": {
                    "passenger_capacity": 4,
                    "luggage_capacity": 2,
                    "hybrid": False,
                    "electric": True,
                    "child_seat": False,
                },
            },
            "fare": {
                "total": 3550,
                "currency": "GBP",
                "gratuity_percent": 0,
                "breakdown": [],
            },
            "external_trip_id": "Ref_123",
            "display_trip_id": "A5TH-R27D",
            "fleet_info": {
                "fleet_id": "82cdc359-beed-45cb-8743-baec84e58b57",
                "name": "PHV Fleet (Robot Fleet GB",
                "logo_url": "https://cdn.karhoo.com/d/images/organisation-logos",
                "description": (
                    "Regional Private Hire Company operating in London and surroundings"
                ),
                "phone_number": "+4489999999",
                "terms_conditions_url": "https://cdn.karhoo.com/d/terms/fleets",
                "email": "dispatch-co@karhoo.com",
            },
            "vehicle": {
                "vehicle_class": "MPV",
                "description": "",
                "vehicle_license_plate": "",
                "driver": {
                    "first_name": "",
                    "last_name": "",
                    "phone_number": "",
                    "photo_url": "",
                    "license_number": "",
                },
                "attributes": {
                    "passenger_capacity": 4,
                    "luggage_capacity": 2,
                    "hybrid": False,
                    "electric": True,
                    "child_seat": False,
                },
            },
            "partner_trip_id": "9975d6f2-75e0-463a-85f8-d6b17d2b0143",
            "comments": "They are waiting by the green door at Fake Street 2a",
            "flight_number": "BA1326",
            "train_number": "",
            "date_booked": "2020-02-17T15:26:59Z",
            "meeting_point": {
                "position": {"latitude": 51.5086692, "longitude": -0.1375291},
                "type": "CURB_SIDE",
                "instructions": (
                    "Meet Driver outside terminal near Bus stop and taxi rank"
                ),
                "note": "",
            },
            "agent": {
                "user_id": "5fc4f43b-2832-466ce-9943-8728589ef9897",
                "user_name": "TestOrg",
                "organisation_id": "3d91a9a7-3e3hc-47ae-be9f-26872c6ce3f8",
                "organisation_name": "Partner_Org",
            },
            "cost_center_reference": "EMEA-sales",
            "cancelled_by": {"first_name": "", "last_name": "", "id": "", "email": ""},
            "follow_code": "47ae-be96ce35fc4f4",
            "meta": {"additionalProp": "string"},
        },
    )

    booking = await karhoo_client.book_trip(
        booking=bookings.Booking(
            meta={"additionalProp": "string"},
            quote_id="9361d590-7472-11e8-82da-0a580a2c041d",
            passengers=passenger.Passengers(
                additional_passengers=0,
                passenger_details=[
                    passenger.PassengerDetails(
                        first_name="John",
                        last_name="Smith",
                        email="john.smith@karhoo.com",
                        phone_number="+4412345678",
                        locale="en_GB",
                    ),
                ],
                luggage=passenger.Luggage(total=0),
            ),
            partner_trip_id="9975d6f2-75e0-463a-85f8-d6b17d2b0143",
            comments="Please let reception know you are there. Will wait in lobby",
            flight_number="BA1326",
            train_number="1326-32",
            cost_center_reference="EMEA-sales",
            train_time="2018-01-02T15:04:00Z",
        ),
    )

    assert booking.id == "00000000-0000-0000-0000-000000000000"


async def test_get_booking_details(
    httpx_mock: pytest_httpx.HTTPXMock,
    karhoo_client: client.KarhooClient,
) -> None:
    httpx_mock.add_response(
        url="https://test_url/v1/bookings/00000000-0000-0000-0000-000000000000",
        status_code=200,
        json={
            "id": "00000000-0000-0000-0000-000000000000",
            "passengers": {
                "additional_passengers": 0,
                "passenger_details": [
                    {
                        "first_name": "John",
                        "last_name": "Smith",
                        "email": "john.smith@karhoo.com",
                        "phone_number": "+4412345678",
                        "locale": "en_GB",
                    },
                ],
                "luggage": {"total": 0},
            },
            "traveller_id": "",
            "status": "CONFIRMED",
            "state_details": "",
            "origin": {
                "display_address": "Gatwick Airport (LGW), South Terminal, London, UK",
                "position": {"latitude": 51.157753, "longitude": -0.1619743},
                "place_id": "k_e4fd1bd3-7890-11e9-a982-0a580a040cc9",
                "poi_type": "ENRICHED",
                "timezone": "london/europe",
            },
            "destination": {
                "display_address": (
                    "Buckingham Palace, Westminster, London SW1A 1AA, UK"
                ),
                "position": {"latitude": 51.5086692, "longitude": -0.1375291},
                "place_id": "EhpCcm93bmVsbCBTdCwgU2hlZmZpZWxkLCBVSw",
                "poi_type": "NOT_SET_POI_TYPE",
                "timezone": "london/europe",
            },
            "date_scheduled": "2020-02-17T15:26:59Z",
            "quote": {
                "type": "FIXED",
                "total": 3550,
                "currency": "GBP",
                "gratuity_percent": 0,
                "breakdown": [],
                "vehicle_class": "Saloon",
                "qta_high_minutes": 3,
                "qta_low_minutes": 3,
                "vehicle_attributes": {
                    "passenger_capacity": 4,
                    "luggage_capacity": 2,
                    "hybrid": False,
                    "electric": True,
                    "child_seat": False,
                },
            },
            "fare": {
                "total": 3550,
                "currency": "GBP",
                "gratuity_percent": 0,
                "breakdown": [],
            },
            "external_trip_id": "Ref_123",
            "display_trip_id": "A5TH-R27D",
            "fleet_info": {
                "fleet_id": "82cdc359-beed-45cb-8743-baec84e58b57",
                "name": "PHV Fleet (Robot Fleet GB",
                "logo_url": "https://cdn.karhoo.com/d/images/organisation-logos",
                "description": (
                    "Regional Private Hire Company operating in London and surroundings"
                ),
                "phone_number": "+4489999999",
                "terms_conditions_url": "https://cdn.karhoo.com/d/terms/fleets",
                "email": "dispatch-co@karhoo.com",
            },
            "vehicle": {
                "vehicle_class": "MPV",
                "description": "",
                "vehicle_license_plate": "",
                "driver": {
                    "first_name": "",
                    "last_name": "",
                    "phone_number": "",
                    "photo_url": "",
                    "license_number": "",
                },
                "attributes": {
                    "passenger_capacity": 4,
                    "luggage_capacity": 2,
                    "hybrid": False,
                    "electric": True,
                    "child_seat": False,
                },
            },
            "partner_trip_id": "9975d6f2-75e0-463a-85f8-d6b17d2b0143",
            "comments": "They are waiting by the green door at Fake Street 2a",
            "flight_number": "BA1326",
            "train_number": "",
            "date_booked": "2020-02-17T15:26:59Z",
            "meeting_point": {
                "position": {"latitude": 51.5086692, "longitude": -0.1375291},
                "type": "CURB_SIDE",
                "instructions": (
                    "Meet Driver outside terminal near Bus stop and taxi rank"
                ),
                "note": "",
            },
            "agent": {
                "user_id": "5fc4f43b-2832-466ce-9943-8728589ef9897",
                "user_name": "TestOrg",
                "organisation_id": "3d91a9a7-3e3hc-47ae-be9f-26872c6ce3f8",
                "organisation_name": "Partner_Org",
            },
            "cost_center_reference": "EMEA-sales",
            "cancelled_by": {"first_name": "", "last_name": "", "id": "", "email": ""},
            "follow_code": "47ae-be96ce35fc4f4",
            "meta": {"property1": "", "property2": "string"},
        },
    )

    booking = await karhoo_client.get_booking_details(
        "00000000-0000-0000-0000-000000000000",
    )

    assert booking.id == "00000000-0000-0000-0000-000000000000"


async def test_cancel_booking_not_found(
    httpx_mock: pytest_httpx.HTTPXMock,
    karhoo_client: client.KarhooClient,
) -> None:
    httpx_mock.add_response(
        url="https://test_url/v1/bookings/00000000-0000-0000-0000-000000000000",
        status_code=404,
        json={
            "code": "K3003",
            "message": "Not found.",
        },
    )

    with pytest.raises(errors.HttpStatusError) as exc:
        await karhoo_client.cancel_booking(
            ident="00000000-0000-0000-0000-000000000000",
            reason="ETA_TOO_LONG",
            explanation="The car was too dirty",
        )

    assert exc.value.body["message"] == "Not found."  # noqa: WPS441


async def test_get_position_of_trip(
    httpx_mock: pytest_httpx.HTTPXMock,
    karhoo_client: client.KarhooClient,
) -> None:
    httpx_mock.add_response(
        url="https://test_url/v1/bookings/00000000-0000-0000-0000-000000000000/track",
        status_code=200,
        json={
            "position": {
                "latitude": 51.157753,
                "longitude": -0.1619743,
            },
            "direction": {
                "kph": 50,
                "heading": 10,
            },
            "origin_eta": 10,
            "destination_eta": 10,
        },
    )

    response = await karhoo_client.get_position_of_trip(
        "00000000-0000-0000-0000-000000000000",
    )

    assert response.origin_eta == 10
    assert response.direction.kph == 50


async def test_get_final_fare(
    httpx_mock: pytest_httpx.HTTPXMock,
    karhoo_client: client.KarhooClient,
) -> None:
    httpx_mock.add_response(
        url="https://test_url/v1/fares/trip/00000000-0000-0000-0000-000000000000",
        status_code=200,
        json={
            "expected_final_time": "2022-12-19T18:13:08.000Z",
            "expected_in": 11318,
            "state": "PENDING",
        },
    )

    response = await karhoo_client.get_final_fare(
        "00000000-0000-0000-0000-000000000000",
    )

    assert response.state == "PENDING"
