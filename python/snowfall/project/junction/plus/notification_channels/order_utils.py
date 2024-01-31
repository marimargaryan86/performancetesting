from collections.abc import Sequence

from google.protobuf import timestamp_pb2

from snowfall.project.junction.plus.service.notifications.v1 import models_pb2
from snowfall.stdlib.format import protobuf


def compress_flights(
    flights: Sequence[models_pb2.AirBooking],
) -> Sequence[models_pb2.AirBooking]:
    if not flights:
        return flights
    analyzed_flights = [flights[0]]
    transfer_limit = 43200  # 12 hours * 3600
    if len(flights) > 1:
        for flight in flights[1:]:
            last_flight = analyzed_flights[-1]
            difference_between_flights = (
                flight.departure_at.seconds - last_flight.arrival_at.seconds
            )
            if difference_between_flights < transfer_limit:
                analyzed_flights.pop()
                analyzed_flights.append(
                    models_pb2.AirBooking(
                        origin=last_flight.origin,
                        origin_iata=last_flight.origin_iata,
                        departure_at=last_flight.departure_at,
                        destination=flight.destination,
                        destination_iata=flight.destination_iata,
                        arrival_at=flight.arrival_at,
                    ),
                )
            else:
                analyzed_flights.append(flight)
    return analyzed_flights


def proto_to_route_identifier(identifier: models_pb2.RouteIdentifier) -> str:
    return identifier.carrier + str(identifier.flight_number)


def proto_to_format_dt(proto: timestamp_pb2.Timestamp) -> str:
    dt = protobuf.protobuf_to_datetime(proto)
    return dt.strftime(
        "%A %d %b %Y %H:%M",
    )
