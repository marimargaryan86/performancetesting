import datetime
import zoneinfo
from unittest import mock

import aiofiles
import pytest
from xsdata.formats.dataclass import parsers
from xsdata.formats.dataclass.parsers import config as parsers_config

from snowfall.project.junction.go.v1 import models_pb2 as go_models
from snowfall.project.junction.rocket.service.providers.silverrail import (
    adapter as silverrail_adapter,
)
from snowfall.project.junction.rocket.service.providers.silverrail import (
    cache,
    train_stations,
)
from snowfall.project.junction.rocket.service.providers.silverrail import (
    pricing as silverrail_pricing,
)
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.amqp import consumer, producer
from snowfall.vendor.silverrail.models import shopping


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


async def get_shopping_point_to_point_response() -> (
    shopping.PointToPointShoppingResponse
):
    parser = parsers.XmlParser(
        config=parsers_config.ParserConfig(fail_on_unknown_properties=False),
    )
    response = await _load_xml_fixture("point_to_point_shopping.xml")

    output: shopping.ShoppingPointToPointShopOutput = parser.from_bytes(
        response,
        shopping.ShoppingPointToPointShopOutput,
    )
    if not output.body or output.body.point_to_point_shopping_response is None:
        raise RuntimeError("Wrong configured fixture")

    return output.body.point_to_point_shopping_response


@pytest.fixture()
async def train_station_repository() -> train_stations.TrainStationRepository:
    return train_stations.TrainStationRepository([
        train_stations.TrainStation(
            name="Paris Gare De Lyon",
            identifier="FRLYS",
            latitude=48.8448404,
            longitude=2.3744416,
            timezone=zoneinfo.ZoneInfo("Europe/Paris"),
        ),
        train_stations.TrainStation(
            name="Lyon Part Dieu",
            identifier="FRXYD",
            latitude=45.7611339,
            longitude=4.8527867,
            timezone=zoneinfo.ZoneInfo("CET"),
        ),
        train_stations.TrainStation(
            name="Paris Bercy",
            identifier="FRPBE",
            latitude=48.8385918,
            longitude=2.3784756,
            timezone=zoneinfo.ZoneInfo("Europe/Paris"),
        ),
    ])


@pytest.fixture()
async def silverrail_result_detail_cache() -> cache.ResultDetailCache:
    return mock.AsyncMock()


@pytest.fixture()
async def silverrail_search_result_generator(
    train_station_repository: train_stations.TrainStationRepository,
    silverrail_result_detail_cache: cache.ResultDetailCache,
) -> silverrail_adapter.SilverrailOffersAdapter:
    return silverrail_adapter.SilverrailOffersAdapter(
        silverrail_client=mock.Mock(
            name="SilverRailClient",
            shopping_point_to_point=mock.AsyncMock(
                name="shopping_point_to_point",
                return_value=await get_shopping_point_to_point_response(),
            ),
        ),
        train_station_repository=train_station_repository,
        ttl=datetime.timedelta(seconds=15),
        result_detail_cache=silverrail_result_detail_cache,
    )


@pytest.fixture()
async def silverrail_offer_matcher(
    train_station_repository: train_stations.TrainStationRepository,
) -> silverrail_adapter.SilverrailOfferMatcher:
    return silverrail_adapter.SilverrailOfferMatcher(
        silverrail_client=mock.Mock(
            name="SilverRailClient",
            shopping_point_to_point=mock.AsyncMock(
                name="shopping_point_to_point",
                return_value=await get_shopping_point_to_point_response(),
            ),
        ),
        train_station_repository=train_station_repository,
    )


@pytest.fixture()
async def silverrail_quote_result_producer() -> producer.Producer:
    return mock.AsyncMock(spec=producer.Producer)


@pytest.fixture()
async def silverrail_quote_task_consumer(
    silverrail_offer_matcher: silverrail_adapter.SilverrailOfferMatcher,
    silverrail_quote_result_producer: producer.Producer,
) -> silverrail_pricing.QuoteTaskConsumer:
    now = datetime.datetime.now(tz=datetime.UTC)
    return silverrail_pricing.QuoteTaskConsumer(
        offer_matcher=silverrail_offer_matcher,
        consumer_obj=mock.AsyncMock(spec=consumer.Consumer),
        quote_result_producer=silverrail_pricing.QuoteResultProducer(
            producer_obj=silverrail_quote_result_producer,
            routing_key="quote-result",
        ),
        result_detail_cache=mock.AsyncMock(
            name="ResultDetailCache",
            fetch=mock.AsyncMock(
                name="fetch",
                return_value=cache.RailResultDetail(
                    origin="FRLYS",
                    destination="FRXYD",
                    outbound_departure_after=now,
                    outbound_departure_before=now + datetime.timedelta(days=2),
                    passenger_dobs=[
                        (now - datetime.timedelta(days=365 * 30)).date(),
                    ],
                    cabin_class=go_models.CabinClass.TYPE_ECONOMY,
                ),
            ),
        ),
        quote_cache=mock.AsyncMock(name="QuoteCache"),
        pay_company_id="fake-pay-company-id",
        ttl=datetime.timedelta(seconds=15),
    )
