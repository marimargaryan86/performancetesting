import math
from collections.abc import Sequence

from snowfall.project.junction.go.service.places.typing import ProviderJson


def calculate_distance(
    p1: tuple[float, float],
    p2: tuple[float, float],
) -> float:
    """Return the great circle distance in meters between two points."""
    lon1, lat1, lon2, lat2 = map(math.radians, (*p1, *p2))
    radius_of_earth_in_metres = 6371000
    dlon = math.sin((lon2 - lon1) / 2) ** 2
    dlat = math.sin((lat2 - lat1) / 2) ** 2
    hav = dlat + math.cos(lat1) * math.cos(lat2) * dlon
    distance = 2 * math.asin(math.sqrt(hav))
    return distance * radius_of_earth_in_metres


def coordinates_within_radius(
    target_coords: tuple[float, float],
    radius: int,
    json_data: Sequence[ProviderJson],
) -> list[str]:
    filtered = filter(
        lambda item: calculate_distance(
            target_coords,
            (item["latitude"], item["longitude"]),
        )
        <= radius,
        json_data,
    )
    return [provider_place["id"] for provider_place in filtered]


def place_within_radius(
    target_coords: tuple[float, float],
    radius: int,
    json_data: Sequence[ProviderJson],
) -> str | None:
    nearest_place = min(
        json_data,
        key=lambda item: calculate_distance(
            target_coords,
            (item["latitude"], item["longitude"]),
        ),
    )
    nearest_coords = (nearest_place["latitude"], nearest_place["longitude"])
    if calculate_distance(target_coords, nearest_coords) <= radius:
        return nearest_place["id"]

    return None
