import datetime
import logging
import os

import pytest

from snowfall.vendor.distribusion import client, enums
from snowfall.vendor.distribusion.models.connections import (
    Connection,
    ConnectionVacancy,
)
from snowfall.vendor.distribusion.models.criterias import (
    ConnectedStationsCriteria,
    ConnectionSeats,
    ConnectionVacancyCriteria,
    CreateOrder,
    FindConnectionsCriteria,
    Passenger,
)

disable_by_default = pytest.mark.skipif(
    os.getenv("DISTRIBUSION_TESTS") != "ENABLED",
    reason="To enable set env variable DISTRIBUSION_TESTS=ENABLED",
)


@disable_by_default
async def test_carriers(distribusion_client: client.DistribusionClient) -> None:
    carriers = await distribusion_client.get_marketing_carriers()
    assert carriers is not None


@disable_by_default
async def test_get_carriers_by_id(
    distribusion_client: client.DistribusionClient,
) -> None:
    marketing_carrier_id = "VICA"
    carrier = await distribusion_client.get_marketing_carrier_details(
        marketing_carrier_id,
    )
    assert carrier is not None


@disable_by_default
async def test_get_carrier_booking_schema(
    distribusion_client: client.DistribusionClient,
) -> None:
    marketing_carrier_id = "VICA"
    booking_schema = await distribusion_client.get_marketing_carrier_booking_schema(
        marketing_carrier_id,
    )
    assert booking_schema.identifier


@disable_by_default
async def test_get_all_carriers_by_id(
    distribusion_client: client.DistribusionClient,
) -> None:
    marketing_carriers = await distribusion_client.get_marketing_carriers()
    assert marketing_carriers

    for marketing_carrier in marketing_carriers:
        carrier = await distribusion_client.get_marketing_carrier_details(
            marketing_carrier.code,
        )
        assert carrier is not None


@disable_by_default
async def test_get_marketing_carrier_stations(
    distribusion_client: client.DistribusionClient,
) -> None:
    stations = await distribusion_client.get_marketing_carrier_stations(
        marketing_carrier_id="VICA",
    )

    assert stations is not None


@disable_by_default
async def test_connections_find(
    distribusion_client: client.DistribusionClient,
) -> None:
    connections = await distribusion_client.find_connections(
        FindConnectionsCriteria(
            departure_stations=["DEBERCBS"],
            arrival_stations=["FRPARPGB"],
            departure_date=datetime.datetime.now(tz=datetime.UTC).date()
            + datetime.timedelta(days=10),
            pax_ages=[30],
            pax=1,
            locale="en",
            currency="EUR",
        ),
    )

    assert connections is not None


@disable_by_default
async def test_city_connections_find(
    distribusion_client: client.DistribusionClient,
) -> None:
    connections = await distribusion_client.find_connections(
        FindConnectionsCriteria(
            departure_stations=["DEBER"],
            arrival_stations=["FRPAR"],
            departure_date=datetime.datetime.now(tz=datetime.UTC).date()
            + datetime.timedelta(days=10),
            pax_ages=[30],
            pax=1,
            locale="en",
            currency="EUR",
        ),
    )

    assert connections is not None


@disable_by_default
async def test_connections_find_round_trip(
    distribusion_client: client.DistribusionClient,
) -> None:
    connections = await distribusion_client.find_connections(
        FindConnectionsCriteria(
            departure_stations=["DEBERCBS"],
            arrival_stations=["FRPARPGB"],
            departure_date=datetime.datetime.now(tz=datetime.UTC).date()
            + datetime.timedelta(days=10),
            return_date=datetime.datetime.now(tz=datetime.UTC).date()
            + datetime.timedelta(days=12),
            pax_ages=[30],
            pax=1,
            locale="en",
            currency="EUR",
        ),
    )

    assert connections is not None


@disable_by_default
async def test_stations(distribusion_client: client.DistribusionClient) -> None:
    stations = await distribusion_client.get_stations()
    assert stations is not None


@disable_by_default
async def test_connection_vacancy(
    distribusion_client: client.DistribusionClient,
) -> None:
    connections = await distribusion_client.get_connection_vacancy(
        ConnectionVacancyCriteria(
            marketing_carrier="VICA",
            departure_station="DEBERCBS",
            arrival_station="FRPARPGB",
            departure_time=datetime.datetime.now(tz=datetime.UTC).replace(
                hour=10,
                minute=18,
            )
            + datetime.timedelta(days=20),
            arrival_time=datetime.datetime.now(tz=datetime.UTC).replace(
                hour=22,
                minute=30,
            )
            + datetime.timedelta(days=20),
            pax=[1],
            passenger_type=["PNOS"],
            currency="EUR",
        ),
    )

    assert connections is not None


@disable_by_default
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
async def test_connection_seats(
    distribusion_client: client.DistribusionClient,
) -> None:
    connections = await distribusion_client.get_connection_seats(
        ConnectionSeats(
            marketing_carrier="VICA",
            departure_station="DEBERCBS",
            arrival_station="FRPARPGB",
            departure_time=datetime.datetime.now(tz=datetime.UTC).replace(
                hour=10,
                minute=18,
            )
            + datetime.timedelta(days=20),
            arrival_time=datetime.datetime.now(tz=datetime.UTC).replace(
                hour=22,
                minute=30,
            )
            + datetime.timedelta(days=20),
        ),
    )

    assert connections is not None


@disable_by_default
async def test_get_booking_by_id(
    distribusion_client: client.DistribusionClient,
) -> None:
    booking_id = "28wfnEhKzGEWqZ02ykHtdw"
    booking_details = await distribusion_client.get_booking_by_id(booking_id)
    assert booking_details.currency == "EUR"


@disable_by_default
async def test_order_create(  # noqa: WPS210
    distribusion_client: client.DistribusionClient,
) -> None:
    departure_station = "DEBERCBS"
    arrival_station = "FRPARPGB"

    connections = await distribusion_client.find_connections(
        FindConnectionsCriteria(
            departure_stations=[departure_station],
            arrival_stations=[arrival_station],
            departure_date=datetime.datetime.now(tz=datetime.UTC).date()
            + datetime.timedelta(days=10),
            pax_ages=[30],
            pax=1,
            locale="en",
            currency="EUR",
        ),
    )

    assert connections
    connection: Connection = connections[0]
    marketing_carrier_code = (
        connection.marketing_carrier.identifier if connection.marketing_carrier else ""
    )
    departure_time = datetime.datetime.fromisoformat(connection.departure_time or "")
    arrival_time = datetime.datetime.fromisoformat(connection.arrival_time or "")

    connection_vacancy_criteria = ConnectionVacancyCriteria(
        marketing_carrier=marketing_carrier_code,
        departure_station=departure_station,
        arrival_station=arrival_station,
        departure_time=departure_time,
        arrival_time=arrival_time,
        pax=[1],
        passenger_type=["PNOS"],
        currency="EUR",
    )

    vacancy: ConnectionVacancy = await distribusion_client.get_connection_vacancy(
        connection_vacancy_criteria,
    )

    assert vacancy.vacant

    order_create_request = CreateOrder(
        marketing_carrier=marketing_carrier_code,
        departure_station=departure_station,
        arrival_station=arrival_station,
        departure_time=departure_time.isoformat(timespec="minutes"),
        arrival_time=arrival_time.isoformat(timespec="minutes"),
        title="mr",
        first_name="Snowfall",
        last_name="Traveller",
        email="andriy.n@snowfalltravel.com",
        phone="4877777777777",
        city="Montreal",
        zip_code="H9G 1B3",
        street_and_number="5 Street",
        execute_payment=True,
        payment_method=enums.PaymentMethod.demand_note,
        total_price=connection.cheapest_total_adult_price or 0,
        pax=1,
        terms_accepted=True,
        locale="en",
        currency="EUR",
        send_customer_email=False,
        fare_class=connection.cheapest_fare_class_code or "",
        passengers=[
            Passenger(
                first_name="Snowfall",
                last_name="Traveller",
                passenger_type="PNOS",
            ),
        ],
    )

    order = await distribusion_client.create_order(order_create_request)
    assert order.identifier
    logging.info("Order ID: %s", order.identifier)

    order_details, raw_data = await distribusion_client.get_order(order.identifier)
    assert order_details.state
    logging.info("Order state: %s", order_details.state)


@disable_by_default
async def test_get_order_by_id(
    distribusion_client: client.DistribusionClient,
) -> None:
    order_id = "VICA-66bbc46a-7bfd-4c5b-bcdd-d984ff247f0b"
    order_details, raw_data = await distribusion_client.get_order(order_id)
    assert order_details.identifier


@disable_by_default
async def test_get_tickets(
    distribusion_client: client.DistribusionClient,
) -> None:
    order_id = "VICA-66bbc46a-7bfd-4c5b-bcdd-d984ff247f0b"
    order_details, raw_data = await distribusion_client.get_order(order_id)
    assert order_details.booking
    assert order_details.booking.identifier

    tickets = await distribusion_client.get_tickets(order_details.booking.identifier)
    assert tickets.ticket_content


@disable_by_default
async def test_get_cancellation_conditions(  # noqa: WPS218
    distribusion_client: client.DistribusionClient,
) -> None:
    order_id = "VICA-66bbc46a-7bfd-4c5b-bcdd-d984ff247f0b"
    order_details, raw_data = await distribusion_client.get_order(order_id)
    assert order_details.booking
    assert order_details.booking.identifier

    cancellation_conditions = await distribusion_client.get_cancellation_conditions(
        order_details.booking.identifier,
    )
    assert cancellation_conditions.identifier
    assert cancellation_conditions.allowed
    assert cancellation_conditions.cutoff
    assert cancellation_conditions.fee is not None


@disable_by_default
async def test_create_cancellation(  # noqa: WPS218
    distribusion_client: client.DistribusionClient,
) -> None:
    order_id = "VICA-4be6700c-4dcd-4513-987b-6d64669367ea"
    order_details, raw_data = await distribusion_client.get_order(order_id)
    assert order_details.booking
    assert order_details.booking.identifier

    cancellation = await distribusion_client.create_cancellation(
        order_details.booking.identifier,
    )
    assert cancellation.identifier
    assert cancellation.total_price
    assert cancellation.total_refund
    assert cancellation.created_at
