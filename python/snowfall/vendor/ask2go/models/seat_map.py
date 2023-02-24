from snowfall.stdlib.v1alpha import seat_maps_pb2
from snowfall.vendor.ask2go.models.base import CamelCaseBaseModel


class SeatMapResponse(CamelCaseBaseModel):
    """To be done."""


def to_seat_map_pb(seat_map_response: SeatMapResponse) -> seat_maps_pb2.SeatMapResult:
    return seat_maps_pb2.SeatMapResult()
