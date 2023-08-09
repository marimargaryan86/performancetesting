from collections.abc import Sequence

from snowfall.project.junction.plus.service.notifications.v1alpha import models_pb2


def compress_flights(  # noqa: WPS210
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
