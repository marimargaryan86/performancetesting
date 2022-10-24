from enum import IntEnum

from snowfall.stdlib.v1alpha import models_pb2


class LocationType(IntEnum):
    """Type of the location."""

    platform = 0
    station = 1
    entrance_exit = 2
    generic_node = 3
    boarding_area = 4


class RouteType(IntEnum):
    """Indicates the type of transportation used on a route."""

    light_rail = 0
    underground_rail_system = 1
    rail = 2
    bus = 3
    ferry = 4
    cable_tram = 5
    cable_transport = 6
    funicular = 7
    trolleybus = 8
    monorail = 9
    railway_service = 100
    high_speed_rail_service = 101
    long_distance_trains = 102
    inter_regional_rail_service = 103
    sleeper_rail_service = 105
    regional_rail_service = 106
    tourist_railway_service = 107
    rail_shuttle_within_complex = 108
    suburban_railway = 109
    coach_service = 200
    international_coach_service = 201
    national_coach_service = 202
    regional_coach_service = 204
    urban_railway_service = 400
    metro_service = 401
    underground_service = 402
    bus_service = 700
    regional_bus_service = 701
    express_bus_service = 702
    local_bus_service = 704
    demand_and_response_bus_service = 715
    trolleybus_service = 800
    tram_service = 900
    water_transport_service = 1000
    air_service = 1100
    ferry_service = 1200
    aerial_lift_service = 1300
    funicular_service = 1400
    communal_taxi_service = 1501
    miscellaneous_service = 1700
    horse_drawn_carriage = 1702


class PickupType(IntEnum):
    """Indicates pickup method."""

    regularly_scheduled_pickup = 0
    no_pickup_available = 1
    phone_agency_to_arrange_pickup = 2
    coordinate_with_driver_to_arrange_pickup = 3


class DropOffType(IntEnum):
    """Indicates drop off method."""

    regularly_scheduled_drop_off = 0
    no_drop_off_available = 1
    phone_agency_to_arrange_drop_off = 2
    coordinate_with_driver_to_arrange_drop_off = 3


_type_mapping = {
    0: models_pb2.Schedule.TYPE_UNSPECIFIED,
    1: models_pb2.Schedule.TYPE_UNSPECIFIED,
    2: models_pb2.Schedule.TYPE_RAIL,
    3: models_pb2.Schedule.TYPE_UNSPECIFIED,
    4: models_pb2.Schedule.TYPE_UNSPECIFIED,
    5: models_pb2.Schedule.TYPE_UNSPECIFIED,
    6: models_pb2.Schedule.TYPE_UNSPECIFIED,
    7: models_pb2.Schedule.TYPE_UNSPECIFIED,
    11: models_pb2.Schedule.TYPE_UNSPECIFIED,
    12: models_pb2.Schedule.TYPE_UNSPECIFIED,
    100: models_pb2.Schedule.TYPE_RAIL,
    101: models_pb2.Schedule.TYPE_RAIL,
    102: models_pb2.Schedule.TYPE_RAIL,
    103: models_pb2.Schedule.TYPE_RAIL,
    104: models_pb2.Schedule.TYPE_RAIL,
    105: models_pb2.Schedule.TYPE_RAIL,
    106: models_pb2.Schedule.TYPE_RAIL,
    107: models_pb2.Schedule.TYPE_RAIL,
    108: models_pb2.Schedule.TYPE_UNSPECIFIED,
    109: models_pb2.Schedule.TYPE_RAIL,
    110: models_pb2.Schedule.TYPE_RAIL,
    111: models_pb2.Schedule.TYPE_RAIL,
    112: models_pb2.Schedule.TYPE_RAIL,
    113: models_pb2.Schedule.TYPE_RAIL,
    114: models_pb2.Schedule.TYPE_RAIL,
    115: models_pb2.Schedule.TYPE_RAIL,
    116: models_pb2.Schedule.TYPE_UNSPECIFIED,
    117: models_pb2.Schedule.TYPE_RAIL,
    200: models_pb2.Schedule.TYPE_UNSPECIFIED,
    201: models_pb2.Schedule.TYPE_UNSPECIFIED,
    202: models_pb2.Schedule.TYPE_UNSPECIFIED,
    203: models_pb2.Schedule.TYPE_UNSPECIFIED,
    204: models_pb2.Schedule.TYPE_UNSPECIFIED,
    205: models_pb2.Schedule.TYPE_UNSPECIFIED,
    206: models_pb2.Schedule.TYPE_UNSPECIFIED,
    207: models_pb2.Schedule.TYPE_UNSPECIFIED,
    208: models_pb2.Schedule.TYPE_UNSPECIFIED,
    209: models_pb2.Schedule.TYPE_UNSPECIFIED,
    400: models_pb2.Schedule.TYPE_UNSPECIFIED,
    401: models_pb2.Schedule.TYPE_UNSPECIFIED,
    402: models_pb2.Schedule.TYPE_UNSPECIFIED,
    403: models_pb2.Schedule.TYPE_UNSPECIFIED,
    404: models_pb2.Schedule.TYPE_UNSPECIFIED,
    405: models_pb2.Schedule.TYPE_UNSPECIFIED,
    700: models_pb2.Schedule.TYPE_UNSPECIFIED,
    701: models_pb2.Schedule.TYPE_UNSPECIFIED,
    702: models_pb2.Schedule.TYPE_UNSPECIFIED,
    703: models_pb2.Schedule.TYPE_UNSPECIFIED,
    704: models_pb2.Schedule.TYPE_UNSPECIFIED,
    705: models_pb2.Schedule.TYPE_UNSPECIFIED,
    706: models_pb2.Schedule.TYPE_UNSPECIFIED,
    707: models_pb2.Schedule.TYPE_UNSPECIFIED,
    708: models_pb2.Schedule.TYPE_UNSPECIFIED,
    709: models_pb2.Schedule.TYPE_UNSPECIFIED,
    710: models_pb2.Schedule.TYPE_UNSPECIFIED,
    711: models_pb2.Schedule.TYPE_UNSPECIFIED,
    712: models_pb2.Schedule.TYPE_UNSPECIFIED,
    713: models_pb2.Schedule.TYPE_UNSPECIFIED,
    714: models_pb2.Schedule.TYPE_UNSPECIFIED,
    715: models_pb2.Schedule.TYPE_UNSPECIFIED,
    716: models_pb2.Schedule.TYPE_UNSPECIFIED,
    800: models_pb2.Schedule.TYPE_UNSPECIFIED,
    900: models_pb2.Schedule.TYPE_UNSPECIFIED,
    901: models_pb2.Schedule.TYPE_UNSPECIFIED,
    902: models_pb2.Schedule.TYPE_UNSPECIFIED,
    903: models_pb2.Schedule.TYPE_UNSPECIFIED,
    904: models_pb2.Schedule.TYPE_UNSPECIFIED,
    905: models_pb2.Schedule.TYPE_UNSPECIFIED,
    906: models_pb2.Schedule.TYPE_UNSPECIFIED,
    1000: models_pb2.Schedule.TYPE_UNSPECIFIED,
    1100: models_pb2.Schedule.TYPE_AIR,
    1200: models_pb2.Schedule.TYPE_UNSPECIFIED,
    1300: models_pb2.Schedule.TYPE_UNSPECIFIED,
    1400: models_pb2.Schedule.TYPE_UNSPECIFIED,
    1500: models_pb2.Schedule.TYPE_UNSPECIFIED,
    1501: models_pb2.Schedule.TYPE_UNSPECIFIED,
    1502: models_pb2.Schedule.TYPE_UNSPECIFIED,
    1503: models_pb2.Schedule.TYPE_UNSPECIFIED,
    1504: models_pb2.Schedule.TYPE_UNSPECIFIED,
    1505: models_pb2.Schedule.TYPE_UNSPECIFIED,
    1506: models_pb2.Schedule.TYPE_UNSPECIFIED,
    1507: models_pb2.Schedule.TYPE_UNSPECIFIED,
    1700: models_pb2.Schedule.TYPE_UNSPECIFIED,
    1702: models_pb2.Schedule.TYPE_UNSPECIFIED,
}


def gtfs_type_to_schedule_type(gtfs_type: int) -> "models_pb2.Schedule.Type.V":
    try:
        return _type_mapping[gtfs_type]
    except KeyError:
        return models_pb2.Schedule.TYPE_UNSPECIFIED
