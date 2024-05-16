from unittest import mock

import httpx

from snowfall.project.junction.go.v1 import models_pb2 as go_models
from snowfall.project.junction.rocket.service.bookings.v1alpha import amqp_pb2
from snowfall.project.junction.rocket.service.bookings.v1alpha import (
    models_pb2 as booking_models,
)
from snowfall.project.junction.rocket.service.providers.silverrail import bookings
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import (
    date_pb2,
    datetime_pb2,
    latlng_pb2,
    money_pb2,
    phone_number_pb2,
    postal_address_pb2,
)


def get_booking_task(passenger_first_name: str) -> amqp_pb2.PlaceBookingTask:
    return amqp_pb2.PlaceBookingTask(
        booking=booking_models.Booking(
            reseller_id="9e693a64-c3fd-4c8c-8af7-0cd817939b38",
            provider_id="be10f208-51f1-4b1a-9cb8-3ad66baa5c74",
            provider_name="Silverrail",
            trip_option=booking_models.TripOption(
                price_quote_id="_c6INHqlc0ypOt1S8JP4Tw-6",
                price=money_pb2.Money(
                    currency_code="EUR",
                    units=31,
                ),
                details=[
                    booking_models.TripOptionDetails(
                        rail=models_pb2.RailResultDetail(
                            outbound_segment=True,
                            segment_sequence=1,
                            origin=go_models.Point(
                                name="FRLYS",
                                coordinates=latlng_pb2.LatLng(
                                    latitude=50.8356748,
                                    longitude=4.3362419,
                                ),
                                time_zone="Europe/Brussels",
                            ),
                            destination=go_models.Point(
                                name="FRXYD",
                                coordinates=latlng_pb2.LatLng(
                                    latitude=51.1997015,
                                    longitude=4.4323348,
                                ),
                                time_zone="Europe/Brussels",
                            ),
                            departure_date=datetime_pb2.DateTime(
                                year=2024,
                                month=6,
                                day=6,
                                hours=14,
                            ),
                        ),
                    ),
                ],
                rules=[],
            ),
            passengers=[
                booking_models.Passenger(
                    first_name=passenger_first_name,
                    last_name="Last",
                    title=booking_models.Passenger.Title.TITLE_MR,
                    gender=booking_models.Passenger.Gender.GENDER_MALE,
                    date_of_birth=date_pb2.Date(
                        year=1981,
                        month=11,
                        day=12,
                    ),
                    doc_details=booking_models.DocumentDetails(
                        issue_county="GB",
                        document_type=booking_models.DocumentDetails.Type.TYPE_PASSPORT,
                        document_number="AR123453",
                        nationality="Armenian",
                        residence_country_code="AM",
                        issue_date=date_pb2.Date(
                            year=2023,
                            month=12,
                            day=6,
                        ),
                        exp_date=date_pb2.Date(
                            year=2033,
                            month=12,
                            day=6,
                        ),
                    ),
                    place_of_birth="Yerevan",
                    lead_passenger=True,
                    contact_details=booking_models.ContactDetails(
                        address=postal_address_pb2.PostalAddress(
                            address_lines=["Street name 7"],
                            postal_code="0052",
                            locality="London",
                        ),
                        phone=phone_number_pb2.PhoneNumber(
                            e164_number="37455111944",
                        ),
                        email="test@example.com",
                    ),
                ),
            ],
        ),
    )


async def test_booking_successful(  # noqa: WPS218
    silverrail_booker: bookings.Booker,
    booking_storage: mock.AsyncMock,
    silverrail_client: mock.AsyncMock,
) -> None:
    expected_reference = "Ty1TTk9XRkFMTC1DQ0EwMDAwVEotUE9VMDAwMDAx"
    task = get_booking_task("First")
    booking = await silverrail_booker.book(task=task)

    assert booking.provider_name == "Silverrail"
    assert booking.provider_id == "fc4f9bbb-69d1-4cef-b8ac-ecd3661abba4"
    assert booking.reseller_id == "9e693a64-c3fd-4c8c-8af7-0cd817939b38"
    assert booking.status == booking_models.Booking.STATUS_CONFIRMED
    assert booking.trip_option.price.units == 31
    assert booking.trip_option.price.currency_code == "EUR"
    assert booking.provider_booking.record_locator == "B-SNOWFALL-CCA0000TJ"
    assert booking.provider_booking.booking_reference == expected_reference
    assert booking.provider_booking.raw_data

    booking_storage.put.assert_awaited()
    path, booking_raw = booking_storage.put.call_args[0]
    assert path.name == expected_reference
    stored_booking = protobuf.AnySerializer[booking_models.Booking]().deserialize(
        booking_raw,
    )
    assert stored_booking == booking

    silverrail_client.add_payment.assert_awaited()
    silverrail_client.confirm_booking.assert_awaited()


async def test_booking_required_request_field_missing(
    silverrail_booker: bookings.Booker,
) -> None:
    task = get_booking_task("")
    booking = await silverrail_booker.book(task=task)

    assert booking.status == booking_models.Booking.STATUS_ERROR
    assert (
        booking.provider_booking.raw_data
        == "RequiredInformationMissingError('FirstName')"
    )


async def test_booking_request_failed(
    silverrail_booker: bookings.Booker,
    silverrail_client: mock.AsyncMock,
) -> None:
    silverrail_client.create_booking_record.side_effect = httpx.HTTPError("Failed!")
    task = get_booking_task("First")
    booking = await silverrail_booker.book(task=task)

    assert booking.status == booking_models.Booking.STATUS_ERROR
    assert booking.provider_booking.raw_data == "HTTPError('Failed!')"


async def test_booking_request_unsuccessful(
    silverrail_booker: bookings.Booker,
    silverrail_client: mock.AsyncMock,
) -> None:
    result = silverrail_client.create_booking_record.return_value
    result.request_status.__dict__["success"] = False
    task = get_booking_task("First")
    booking = await silverrail_booker.book(task=task)

    assert booking.status == booking_models.Booking.STATUS_ERROR
    assert booking.provider_booking.raw_data


async def test_booking_required_response_field_missing(
    silverrail_booker: bookings.Booker,
    silverrail_client: mock.AsyncMock,
) -> None:
    result = silverrail_client.create_booking_record.return_value
    result.booking_record.revenue_total.__dict__["value"] = None
    task = get_booking_task("First")
    booking = await silverrail_booker.book(task=task)

    assert booking.status == booking_models.Booking.STATUS_ERROR
    assert booking.provider_booking.raw_data


async def test_booking_add_payment_unsuccessful(
    silverrail_booker: bookings.Booker,
    silverrail_client: mock.AsyncMock,
) -> None:
    result = silverrail_client.add_payment.return_value
    result.request_status.__dict__["success"] = False
    task = get_booking_task("First")
    booking = await silverrail_booker.book(task=task)

    assert booking.status == booking_models.Booking.STATUS_ERROR


async def test_booking_confirm_booking_unsuccessful(
    silverrail_booker: bookings.Booker,
    silverrail_client: mock.AsyncMock,
) -> None:
    result = silverrail_client.confirm_booking.return_value
    result.request_status.__dict__["success"] = False
    task = get_booking_task("First")
    booking = await silverrail_booker.book(task=task)

    assert booking.status == booking_models.Booking.STATUS_ERROR
