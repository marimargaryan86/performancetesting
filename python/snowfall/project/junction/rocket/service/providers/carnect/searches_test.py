import datetime
import math
from unittest import mock

import aiofiles
import pytest
from xsdata.formats.dataclass import parsers
from xsdata.formats.dataclass.parsers import config as parsers_config

from snowfall.project.junction.go.v1 import models_pb2 as common_pb2
from snowfall.project.junction.rocket.service.providers.carnect import (
    constants,
    criteria,
    searches,
)
from snowfall.stdlib import string
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.v1 import latlng_pb2
from snowfall.vendor.carnect.models import service as carnect_service


async def get_avail_rate_response() -> carnect_service.ServiceSoapGetVehAvailRateOutput:
    parser = parsers.XmlParser(
        config=parsers_config.ParserConfig(fail_on_unknown_properties=False),
    )
    response = await _load_xml_fixture("get_avail_rate.xml")
    return parser.from_bytes(response, carnect_service.ServiceSoapGetVehAvailRateOutput)


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
        ttl=datetime.timedelta(seconds=15),
    )


async def test_successful(  # noqa: WPS218
    search_result_generator: searches.SearchResultGenerator,
) -> None:
    search_task = criteria.Criteria(
        search_id=string.uuid(),
        origin=common_pb2.Point(
            coordinates=latlng_pb2.LatLng(
                latitude=50.89369066956447,
                longitude=4.47136870945399,
            ),
        ),
        destination=common_pb2.Point(
            coordinates=latlng_pb2.LatLng(
                latitude=48.96691462802318,
                longitude=2.52817297961273,
            ),
        ),
        pickup_datetime=datetime.datetime.now(tz=datetime.UTC),
        return_datetime=datetime.datetime.now(tz=datetime.UTC),
        driver_age=50,
    )
    results = [
        result
        async for result in search_result_generator.gather_search_results(search_task)
    ]

    assert len(results) == 114

    result = results[0]
    assert len(result.offers) == 1
    assert len(result.result_details) == 1
    assert result.provider_id == str(constants.PROVIDER_ID)

    result_detail = result.result_details[0]
    assert math.isclose(result_detail.car_rental.origin.coordinates.latitude, 50.846541)
    assert math.isclose(result_detail.car_rental.origin.coordinates.longitude, 4.351684)
    assert math.isclose(
        result_detail.car_rental.destination.coordinates.latitude,
        49.003526,
    )
    assert math.isclose(
        result_detail.car_rental.destination.coordinates.longitude,
        2.569589,
    )

    offer = result.offers[0]
    assert offer.price.units == 68
    assert offer.price.currency_code == "EUR"

    assert (
        result_detail.car_rental.image_url
        == "https://vehicles.carhire-solutions.com/371/small/48252_MBMR.jpg"
    )
    assert result_detail.car_rental.model == "A HYUNDAI I10"
    assert result_detail.car_rental.seats_count == 4
    assert result_detail.car_rental.doors_count == 2
    assert result_detail.car_rental.transmission == "Manual"
    assert result_detail.car_rental.baggage_quantity == 1
    assert result_detail.car_rental.vehicle_type == "Car"
    assert result_detail.car_rental.vendor == "Hertz"
    assert result_detail.car_rental.unlimited_mileage
    assert result_detail.car_rental.air_conditioner
