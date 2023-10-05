import datetime

from snowfall.project.junction.plus.notification_channels import order_utils
from snowfall.project.junction.plus.service.notifications.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import latlng_pb2

_latitude = 37.9362
_longitude = 23.948


async def test_trip_compressor_for_single_trip() -> None:
    compressed_trip = order_utils.compress_flights(
        [
            models_pb2.AirBooking(
                departure_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=8),
                ),
                arrival_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=9),
                ),
                origin=models_pb2.Location(
                    name="Zvartnots International Airport",
                    coordinates=latlng_pb2.LatLng(
                        latitude=_latitude,
                        longitude=_longitude,
                    ),
                ),
                destination=models_pb2.Location(
                    name="Paris Charles de Gaulle Airport",
                    coordinates=latlng_pb2.LatLng(
                        latitude=_latitude,
                        longitude=_longitude,
                    ),
                ),
                origin_iata="EVN",
                destination_iata="CDG",
                route_identifier=models_pb2.RouteIdentifier(
                    carrier="U2",
                    flight_number=2440,
                ),
                cabin_class="1stClassCabin",
            ),
        ],
    )
    assert len(compressed_trip) == 1


async def test_trip_compressor_for_transfer_trip() -> None:
    compressed_trip = order_utils.compress_flights(
        [
            models_pb2.AirBooking(
                departure_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=8),
                ),
                arrival_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=9),
                ),
                origin=models_pb2.Location(
                    name="Zvartnots International Airport",
                    coordinates=latlng_pb2.LatLng(
                        latitude=_latitude,
                        longitude=_longitude,
                    ),
                ),
                destination=models_pb2.Location(
                    name="Paris Charles de Gaulle Airport",
                    coordinates=latlng_pb2.LatLng(
                        latitude=_latitude,
                        longitude=_longitude,
                    ),
                ),
                origin_iata="EVN",
                destination_iata="CDG",
                route_identifier=models_pb2.RouteIdentifier(
                    carrier="U2",
                    flight_number=2440,
                ),
                cabin_class="1stClassCabin",
            ),
            models_pb2.AirBooking(
                departure_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=9),
                ),
                arrival_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(tz=datetime.UTC)
                    + datetime.timedelta(days=10),
                ),
                origin=models_pb2.Location(
                    name="Zvartnots International Airport",
                    coordinates=latlng_pb2.LatLng(
                        latitude=_latitude,
                        longitude=_longitude,
                    ),
                ),
                destination=models_pb2.Location(
                    name="Paris Charles de Gaulle Airport",
                    coordinates=latlng_pb2.LatLng(
                        latitude=_latitude,
                        longitude=_longitude,
                    ),
                ),
                origin_iata="CDG",
                destination_iata="LTN",
                route_identifier=models_pb2.RouteIdentifier(
                    carrier="U2",
                    flight_number=2440,
                ),
                cabin_class="1stClassCabin",
            ),
        ],
    )
    assert len(compressed_trip) == 1


async def test_trip_compressor_for_round_trip() -> None:
    compressed_trip = order_utils.compress_flights(
        [
            models_pb2.AirBooking(
                departure_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=8),
                ),
                arrival_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=9),
                ),
                origin=models_pb2.Location(
                    name="Zvartnots International Airport",
                    coordinates=latlng_pb2.LatLng(
                        latitude=_latitude,
                        longitude=_longitude,
                    ),
                ),
                destination=models_pb2.Location(
                    name="Paris Charles de Gaulle Airport",
                    coordinates=latlng_pb2.LatLng(
                        latitude=_latitude,
                        longitude=_longitude,
                    ),
                ),
                origin_iata="EVN",
                destination_iata="CDG",
                route_identifier=models_pb2.RouteIdentifier(
                    carrier="U2",
                    flight_number=2440,
                ),
                cabin_class="1stClassCabin",
            ),
            models_pb2.AirBooking(
                departure_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(tz=datetime.UTC)
                    + datetime.timedelta(days=20),
                ),
                arrival_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(tz=datetime.UTC)
                    + datetime.timedelta(days=21),
                ),
                origin=models_pb2.Location(
                    name="Zvartnots International Airport",
                    coordinates=latlng_pb2.LatLng(
                        latitude=_latitude,
                        longitude=_longitude,
                    ),
                ),
                destination=models_pb2.Location(
                    name="Paris Charles de Gaulle Airport",
                    coordinates=latlng_pb2.LatLng(
                        latitude=_latitude,
                        longitude=_longitude,
                    ),
                ),
                origin_iata="CDG",
                destination_iata="EVN",
                route_identifier=models_pb2.RouteIdentifier(
                    carrier="U2",
                    flight_number=2440,
                ),
                cabin_class="1stClassCabin",
            ),
        ],
    )
    assert len(compressed_trip) == 2


async def test_trip_compressor_for_multi_city_trip() -> None:
    compressed_trip = order_utils.compress_flights(
        [
            models_pb2.AirBooking(
                departure_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=8),
                ),
                arrival_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=9),
                ),
                origin=models_pb2.Location(
                    name="Zvartnots International Airport",
                    coordinates=latlng_pb2.LatLng(
                        latitude=_latitude,
                        longitude=_longitude,
                    ),
                ),
                destination=models_pb2.Location(
                    name="Paris Charles de Gaulle Airport",
                    coordinates=latlng_pb2.LatLng(
                        latitude=_latitude,
                        longitude=_longitude,
                    ),
                ),
                origin_iata="EVN",
                destination_iata="CDG",
                route_identifier=models_pb2.RouteIdentifier(
                    carrier="U2",
                    flight_number=2440,
                ),
                cabin_class="1stClassCabin",
            ),
            models_pb2.AirBooking(
                departure_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(tz=datetime.UTC)
                    + datetime.timedelta(days=20),
                ),
                arrival_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(tz=datetime.UTC)
                    + datetime.timedelta(days=21),
                ),
                origin=models_pb2.Location(
                    name="Zvartnots International Airport",
                    coordinates=latlng_pb2.LatLng(
                        latitude=_latitude,
                        longitude=_longitude,
                    ),
                ),
                destination=models_pb2.Location(
                    name="Paris Charles de Gaulle Airport",
                    coordinates=latlng_pb2.LatLng(
                        latitude=_latitude,
                        longitude=_longitude,
                    ),
                ),
                origin_iata="CDG",
                destination_iata="LTN",
                route_identifier=models_pb2.RouteIdentifier(
                    carrier="U2",
                    flight_number=2440,
                ),
                cabin_class="1stClassCabin",
            ),
        ],
    )
    assert len(compressed_trip) == 2
