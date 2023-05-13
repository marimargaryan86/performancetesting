from enum import Enum


class _StringableIntEnum(Enum):
    def __str__(self) -> str:
        return str(self.value)


class LocationType(_StringableIntEnum):
    """Type of the location."""

    platform = 0
    station = 1
    entrance_exit = 2
    generic_node = 3
    boarding_area = 4


class RouteType(_StringableIntEnum):
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
    ferry_service = 1200
    aerial_lift_service = 1300
    funicular_service = 1400
    communal_taxi_service = 1501
    miscellaneous_service = 1700
    horse_drawn_carriage = 1702


class PickupType(_StringableIntEnum):
    """Indicates pickup method."""

    regularly_scheduled_pickup = 0
    no_pickup_available = 1
    phone_agency_to_arrange_pickup = 2
    coordinate_with_driver_to_arrange_pickup = 3


class DropOffType(_StringableIntEnum):
    """Indicates drop off method."""

    regularly_scheduled_drop_off = 0
    no_drop_off_available = 1
    phone_agency_to_arrange_drop_off = 2
    coordinate_with_driver_to_arrange_drop_off = 3
