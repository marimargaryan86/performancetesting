import datetime
import os

import pytest

from snowfall.vendor.distribusion import client
from snowfall.vendor.distribusion.models.criterias import (
    ConnectedStationsCriteria,
    ConnectionSeats,
    ConnectionVacancyCriteria,
    FindConnectionsCriteria,
)

disable_by_default = pytest.mark.skipif(
    os.getenv("DISTRIBUSION_TESTS") != "ENABLED",
    reason="To enable set env variable DISTRIBUSION_TESTS=ENABLED",
)


@disable_by_default
@pytest.mark.asyncio
async def test_carriers(distribusion_client: client.DistribusionClient) -> None:
    carriers = await distribusion_client.get_marketing_carriers()
    assert carriers is not None


@disable_by_default
@pytest.mark.asyncio
async def test_get_carriers_by_id(
    distribusion_client: client.DistribusionClient,
) -> None:
    marketing_carrier_id = "VICA"
    carrier = await distribusion_client.get_marketing_carrier_details(
        marketing_carrier_id,
    )
    assert carrier is not None


@disable_by_default
@pytest.mark.asyncio
async def test_get_marketing_carrier_stations(
    distribusion_client: client.DistribusionClient,
) -> None:
    stations = await distribusion_client.get_marketing_carrier_stations(
        marketing_carrier_id="VICA",
    )

    assert stations is not None


@disable_by_default
@pytest.mark.asyncio
async def test_connections_find(
    distribusion_client: client.DistribusionClient,
) -> None:
    connections = await distribusion_client.find_connections(
        FindConnectionsCriteria(
            departure_stations=["DEBERCBS"],
            arrival_stations=["FRPARPGB"],
            departure_date=datetime.date.today() + datetime.timedelta(days=20),
            pax=1,
            locale="en",
            currency="EUR",
        ),
    )

    assert connections is not None


@disable_by_default
@pytest.mark.asyncio
async def test_stations(distribusion_client: client.DistribusionClient) -> None:
    stations = await distribusion_client.get_stations()
    assert stations is not None


@disable_by_default
@pytest.mark.asyncio
async def test_connection_vacancy(
    distribusion_client: client.DistribusionClient,
) -> None:
    connections = await distribusion_client.get_connection_vacancy(
        ConnectionVacancyCriteria(
            marketing_carrier="VICA",
            departure_station="DEBERCBS",
            arrival_station="FRPARPGB",
            departure_time=datetime.datetime.now().replace(hour=10, minute=18)
            + datetime.timedelta(days=20),
            arrival_time=datetime.datetime.now().replace(hour=22, minute=30)
            + datetime.timedelta(days=20),
            pax=[1],
            passenger_type=["PNOS"],
            locale="en",
            currency="EUR",
        ),
    )

    assert connections is not None


@disable_by_default
@pytest.mark.asyncio
async def test_get_connected_stations(
    distribusion_client: client.DistribusionClient,
) -> None:
    connections = await distribusion_client.get_connected_stations(
        ConnectedStationsCriteria(
            page_size=100,
            next_page="GBLONLPB-GBLONLHT",
            carrier_code="VICA",
        ),
    )

    assert connections is not None


@disable_by_default
@pytest.mark.asyncio
async def test_connection_seats(
    distribusion_client: client.DistribusionClient,
) -> None:
    connections = await distribusion_client.get_connection_seats(
        ConnectionSeats(
            marketing_carrier="VICA",
            departure_station="DEBERCBS",
            arrival_station="FRPARPGB",
            departure_time=datetime.datetime.now().replace(hour=10, minute=18)
            + datetime.timedelta(days=20),
            arrival_time=datetime.datetime.now().replace(hour=22, minute=30)
            + datetime.timedelta(days=20),
        ),
    )

    assert connections is not None
