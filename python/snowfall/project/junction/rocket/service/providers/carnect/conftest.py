import datetime
import uuid
from collections.abc import AsyncIterator
from typing import Any
from unittest import mock

import aiofiles
import orjson
import pytest
import pytest_asyncio
from xsdata.formats.dataclass import parsers
from xsdata.formats.dataclass.parsers import config as parsers_config

from snowfall.project.junction.go.v1 import models_pb2 as go_models_pb2
from snowfall.project.junction.rocket.service.bookings.v1alpha import (
    amqp_pb2 as booking_amqp_pb2,
)
from snowfall.project.junction.rocket.service.bookings.v1alpha import (
    models_pb2 as booking_models_pb2,
)
from snowfall.project.junction.rocket.service.providers.carnect import (
    bookings as carnect_bookings,
)
from snowfall.project.junction.rocket.service.providers.carnect import (
    cache,
    pricing,
    searches,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    amqp_pb2,
    models_pb2,
)
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.amqp import consumer, types
from snowfall.stdlib.v1 import (
    date_pb2,
    datetime_pb2,
    latlng_pb2,
    money_pb2,
    phone_number_pb2,
    postal_address_pb2,
)
from snowfall.vendor.carnect.models import service as carnect_service

PAY_COMPANY_ID = "0b4d5313-ce67-4532-9885-f32f204aa17c"


@pytest_asyncio.fixture()
async def consumer_mock() -> pricing.QuoteTaskConsumer:
    return pricing.QuoteTaskConsumer(
        consumer_obj=mock.AsyncMock(spec=consumer.Consumer),
        quote_result_producer=mock.AsyncMock(spec=consumer.Consumer),
        search_result_cache=mock.AsyncMock(
            name="SearchResultCache",
            fetch=mock.AsyncMock(
                name="fetch",
                return_value=cache.CarRentalResultDetail(
                    origin=cache.Coordinates(
                        latitude=50.846541,
                        longitude=4.351684,
                    ),
                    destination=cache.Coordinates(
                        latitude=49.003526,
                        longitude=2.569589,
                    ),
                    departure_at=datetime.datetime(
                        2024,
                        4,
                        8,
                        12,
                        11,
                        0,
                        tzinfo=datetime.UTC,
                    ),
                    arrival_at=datetime.datetime(
                        2024,
                        4,
                        8,
                        12,
                        13,
                        0,
                        tzinfo=datetime.UTC,
                    ),
                    driver_age=37,
                    model="A HYUNDAI I10",
                    seats_count=4,
                    doors_count=2,
                    transmission="Manual",
                    baggage_quantity=1,
                    vehicle_type="Car",
                    vendor_name="Hertz",
                    vendor_code="ZE",
                ),
            ),
        ),
        quote_cache=mock.AsyncMock(name="QuoteCache"),
        carnect_client=mock.AsyncMock(
            name="CarnectClient",
            get_avail_rate=mock.AsyncMock(
                name="get_avail_rate",
                return_value=await get_avail_rate_response(),
            ),
        ),
        carnect_config=mock.Mock(name="CarnectConfig"),
        ttl=datetime.timedelta(minutes=30),
        pay_company_id=PAY_COMPANY_ID,
    )


@pytest.fixture()
async def search_result_generator() -> searches.SearchResultGenerator:
    return searches.SearchResultGenerator(
        carnect_client=mock.Mock(
            name="CarnectClient",
            get_avail_rate=mock.AsyncMock(
                name="get_avail_rate",
                return_value=await get_avail_rate_response(),
            ),
        ),
        carnect_config=mock.Mock(name="CarnectConfig"),
        search_result_cache=mock.AsyncMock(name="SearchResultCache"),
        ttl=datetime.timedelta(seconds=15),
        pay_company_id=PAY_COMPANY_ID,
    )


@pytest_asyncio.fixture
async def mock_message() -> AsyncIterator[types.Message[amqp_pb2.QuoteTask]]:
    offer_id = "65df9a88-bfb1-482d-9061-37f9c4ed989e"
    price = money_pb2.Money(currency_code="USD", units=100)
    with mock.patch("snowfall.stdlib.transport.amqp.types.Message") as msg:
        message = msg.return_value
        message.body = amqp_pb2.QuoteTask(
            quote=models_pb2.Quote(
                id="4530844688",
                pay_company_id=PAY_COMPANY_ID,
                total_price=price,
                offer_ids=[offer_id],
                quoted_offers=[
                    models_pb2.QuotedOffer(
                        offer_id=offer_id,
                        price=price,
                        price_breakdown=[
                            models_pb2.PriceBreakdown(
                                price=money_pb2.Money(currency_code="USD", units=100),
                                breakdown_type=models_pb2.PriceBreakdown.BREAKDOWN_TYPE_UNSPECIFIED,
                            ),
                        ],
                        conditional_prices=[
                            models_pb2.ConditionalPrice(
                                price=money_pb2.Money(currency_code="USD", units=100),
                                description="Description",
                                included_in_total=True,
                            ),
                        ],
                        rules=[
                            models_pb2.FareRule(
                                title="Test title",
                                body="Test Body",
                            ),
                        ],
                        required_documents=[
                            models_pb2.QuotedOffer.REQUIRED_DATE_OF_BIRTH,
                        ],
                    ),
                ],
            ),
            reseller_id="mock_reseller_id",
        )

        yield message


@pytest.fixture()
async def storage() -> AsyncIterator[filesystem.Storage]:
    async with filesystem.Storage.from_dsn("memory://") as storage_obj:
        yield storage_obj


@pytest_asyncio.fixture
async def booking_task_mock() -> (
    AsyncIterator[types.Message[booking_amqp_pb2.PlaceBookingTask]]
):
    with mock.patch("snowfall.stdlib.transport.amqp.types.Message") as msg:
        message = msg.return_value
        message.ack = mock.AsyncMock(name="ack", return_value=None)
        message.body = booking_amqp_pb2.PlaceBookingTask(
            booking=booking_models_pb2.Booking(
                reseller_id="9e693a64-c3fd-4c8c-8af7-0cd817939b38",
                provider_id="fc4f9bbb-69d1-4cef-b8ac-ecd3661abba4",
                provider_name="Carnect",
                trip_option=booking_models_pb2.TripOption(
                    price_quote_id="_c6INHqlc0ypOt1S8JP4Tw-6",
                    price=money_pb2.Money(
                        currency_code="EUR",
                        units=328,
                    ),
                    details=[
                        booking_models_pb2.TripOptionDetails(
                            car_rental=models_pb2.CarRentalResultDetail(
                                origin=go_models_pb2.Point(
                                    name="Yerevan",
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=4.9041,
                                        longitude=52.3676,
                                    ),
                                    time_zone="Europe/Amsterdam",
                                ),
                                destination=go_models_pb2.Point(
                                    name="Tbilisi",
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=4.9041,
                                        longitude=52.3676,
                                    ),
                                    time_zone="Europe/Amsterdam",
                                ),
                                pickup_at=datetime_pb2.DateTime(
                                    year=2024,
                                    month=5,
                                    day=5,
                                    hours=14,
                                    minutes=0,
                                    seconds=0,
                                    nanos=0,
                                ),
                                return_at=datetime_pb2.DateTime(
                                    year=2024,
                                    month=5,
                                    day=6,
                                    hours=14,
                                    minutes=0,
                                    seconds=0,
                                    nanos=0,
                                ),
                            ),
                        ),
                    ],
                    rules=[],
                ),
                passengers=[
                    booking_models_pb2.Passenger(
                        first_name="First",
                        last_name="Last",
                        title=booking_models_pb2.Passenger.Title.TITLE_MR,
                        gender=booking_models_pb2.Passenger.Gender.GENDER_MALE,
                        date_of_birth=date_pb2.Date(
                            year=1996,
                            month=11,
                            day=12,
                        ),
                        doc_details=booking_models_pb2.DocumentDetails(
                            issue_county="GB",
                            document_type=booking_models_pb2.DocumentDetails.Type.TYPE_PASSPORT,
                            document_number="AR123453",
                            nationality="Armenian",
                            residence_country_code="AM",
                        ),
                        place_of_birth="Yerevan",
                        lead_passenger=True,
                        contact_details=booking_models_pb2.ContactDetails(
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

        yield message


@pytest_asyncio.fixture()
async def booking_consumer_mock(
    storage: filesystem.Storage,
) -> carnect_bookings.Consumer:
    return carnect_bookings.Consumer(
        consumer_obj=mock.AsyncMock(spec=consumer.Consumer),
        producer_obj=mock.AsyncMock(spec=consumer.Consumer),
        booker=carnect_bookings.Booker(
            quote_cache=mock.AsyncMock(
                name="QuoteCache",
                fetch=mock.AsyncMock(
                    name="fetch",
                    return_value=cache.PriceQuote(quote_id="_c6INHqlc0ypOt1S8JP4Tw-6"),
                ),
            ),
            booking_storage=storage,
            carnect_client=mock.AsyncMock(
                name="CarnectClient",
                reservation=mock.AsyncMock(
                    name="reservation",
                    return_value=await get_reservation_response(),
                ),
            ),
            carnect_config=mock.Mock(name="CarnectConfig"),
            provider_id=uuid.UUID("fc4f9bbb-69d1-4cef-b8ac-ecd3661abba4"),
            provider_name="Carnect",
        ),
    )


@pytest_asyncio.fixture()
async def cancellation_handler_mock() -> carnect_bookings.CancellationHandler:
    return carnect_bookings.CancellationHandler(
        carnect_client=mock.AsyncMock(
            name="CarnectClient",
            cancel_reservation=mock.AsyncMock(
                name="cancel_reservation",
                return_value=await get_cancellation_response(),
            ),
            retrieve_reservation=mock.AsyncMock(
                name="cancel_reservation",
                return_value=await get_retrieve_reservation_response(),
            ),
        ),
        carnect_config=mock.Mock(name="CarnectConfig"),
    )


@pytest.fixture()
async def search_criteria() -> models_pb2.Search:
    data = await load_json_fixture("search_criteria.json")

    return models_pb2.Search(
        id=data["id"],
        car_rental=models_pb2.CarRental(**data["car_rental"]),
    )


async def _load_xml_fixture(
    file_name: str,
    package: str | None = None,
) -> bytes:
    if not package:
        package = __name__

    file_path = filesystem.resource_path(
        package=package,
        resource="fixtures/{file_name}.xml".format(
            file_name=file_name.removesuffix(".xml"),
        ),
    )

    async with aiofiles.open(file_path, "rb") as file_handle:
        return await file_handle.read()


async def load_json_fixture(
    file_name: str,
    package: str | None = None,
) -> Any:
    if not package:
        package = __name__

    file_path = filesystem.resource_path(
        package=package,
        resource="fixtures/{file_name}.json".format(
            file_name=file_name.removesuffix(".json"),
        ),
    )

    async with aiofiles.open(file_path) as json_file:
        return orjson.loads(await json_file.read())


async def get_avail_rate_response() -> carnect_service.ServiceSoapGetVehAvailRateOutput:
    parser = parsers.XmlParser(
        config=parsers_config.ParserConfig(fail_on_unknown_properties=False),
    )
    response = await _load_xml_fixture("get_avail_rate.xml")
    return parser.from_bytes(response, carnect_service.ServiceSoapGetVehAvailRateOutput)


async def get_reservation_response() -> tuple[Any, bytes]:
    parser = parsers.XmlParser(
        config=parsers_config.ParserConfig(fail_on_unknown_properties=False),
    )
    response = await _load_xml_fixture("reservation.xml")
    return parser.from_bytes(
        response,
        carnect_service.ServiceSoapGetVehReservationOutput,
    ), response


async def get_cancellation_response() -> (
    carnect_service.ServiceSoapGetVehCancelReservationOutput
):
    parser = parsers.XmlParser(
        config=parsers_config.ParserConfig(fail_on_unknown_properties=False),
    )
    response = await _load_xml_fixture("cancellation_result.xml")
    return parser.from_bytes(
        response,
        carnect_service.ServiceSoapGetVehCancelReservationOutput,
    )


async def get_retrieve_reservation_response() -> (
    carnect_service.ServiceSoapGetVehRetReservationOutput
):
    parser = parsers.XmlParser(
        config=parsers_config.ParserConfig(fail_on_unknown_properties=False),
    )
    response = await _load_xml_fixture("retrieve_reservation_result.xml")
    return parser.from_bytes(
        response,
        carnect_service.ServiceSoapGetVehRetReservationOutput,
    )
