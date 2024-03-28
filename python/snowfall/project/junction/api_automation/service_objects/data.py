from collections.abc import Mapping
from typing import Any

from snowfall.project.junction.api_automation.service_objects.helper import (
    get_nested_attribute,
)


class BaseResult(object):
    def __init__(self, data: Mapping[str, Any]):
        self._data = data

    @property
    def data(self) -> str:
        return self._data["data"]


class PlaceData(BaseResult):
    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self._data = data

    @property
    def id(self) -> str:
        return get_nested_attribute(self._data, "data.0.id")

    @property
    def name(self) -> str:
        return get_nested_attribute(self._data, "data.0.attributes.name")

    @property
    def latitude(self) -> float:
        return get_nested_attribute(self._data, "data.0.attributes.latitude")

    @property
    def longitude(self) -> float:
        return get_nested_attribute(self._data, "data.0.attributes.longitude")

    @property
    def country_code(self) -> str:
        return get_nested_attribute(self._data, "data.0.attributes.countryCode")


class AirResultData(BaseResult):
    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self._data = data

    @property
    def id(self) -> str:
        return get_nested_attribute(self._data, "data.id")
