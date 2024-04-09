import datetime
from collections.abc import AsyncIterator
from unittest import mock

import aiofiles
import pytest
import pytest_asyncio
from xsdata.formats.dataclass import parsers
from xsdata.formats.dataclass.parsers import config as parsers_config

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
from snowfall.stdlib.v1 import money_pb2
from snowfall.vendor.carnect.models import service as carnect_service


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
    )


@pytest_asyncio.fixture
async def mock_message() -> AsyncIterator[types.Message[amqp_pb2.QuoteTask]]:
    with mock.patch("snowfall.stdlib.transport.amqp.types.Message") as msg:
        message = msg.return_value
        message.body = amqp_pb2.QuoteTask(
            quote=models_pb2.Quote(
                id="4530844688",
                price=money_pb2.Money(currency_code="USD", units=100),
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
                required_documents=[models_pb2.Quote.REQUIRED_DATE_OF_BIRTH],
            ),
            reseller_id="mock_reseller_id",
        )

        yield message


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


async def get_avail_rate_response() -> carnect_service.ServiceSoapGetVehAvailRateOutput:
    parser = parsers.XmlParser(
        config=parsers_config.ParserConfig(fail_on_unknown_properties=False),
    )
    response = await _load_xml_fixture("get_avail_rate.xml")
    return parser.from_bytes(response, carnect_service.ServiceSoapGetVehAvailRateOutput)
