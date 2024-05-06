from collections.abc import Mapping
from typing import Any

from snowfall.project.junction.api_automation.service_objects.helper import (
    get_nested_attribute,
)


class BaseResult:
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
        return get_nested_attribute(self._data, "data.id")

    @property
    def name(self) -> str:
        return get_nested_attribute(self._data, "data.attributes.name")

    @property
    def latitude(self) -> float:
        return get_nested_attribute(self._data, "data.attributes.latitude")

    @property
    def longitude(self) -> float:
        return get_nested_attribute(self._data, "data.attributes.longitude")

    @property
    def country_code(self) -> str:
        return get_nested_attribute(self._data, "data.attributes.countryCode")

    @property
    def country_name(self) -> str:
        return get_nested_attribute(self._data, "data.attributes.countryName")

    @property
    def iata_code(self) -> str:
        return get_nested_attribute(self._data, "data.attributes.iataCode")


class PlaceListData(BaseResult):
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

    @property
    def country_name(self) -> str:
        return get_nested_attribute(self._data, "data.0.attributes.countryName")

    @property
    def place_type(self) -> str:
        return get_nested_attribute(self._data, "data.0.attributes.placeType")

    @property
    def iata_code(self) -> str:
        return get_nested_attribute(self._data, "data.0.attributes.iataCode")

    @property
    def place_to_search_within(self) -> str:
        return get_nested_attribute(self._data, "data.0.attributes.iataCode")

    @property
    def next_link(self) -> str:
        return get_nested_attribute(self._data, "links.next")

    @property
    def items(self) -> list[dict[str, Any]]:
        return get_nested_attribute(self._data, "data")


class FlightSearchResult:
    def __init__(self, data: Mapping[str, Any]):
        self._data = data

    @property
    def id(self) -> str:
        return get_nested_attribute(self._data, "data.id")

    @property
    def status(self) -> str:
        return get_nested_attribute(self._data, "data.attributes.status")


class FlightOffersResult(BaseResult):
    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self._data = data

    @property
    def id(self) -> str:
        return get_nested_attribute(self._data, "id")

    @property
    def offer_ids(self) -> list[str]:
        return [
            get_nested_attribute(offer, "id")
            for offer in get_nested_attribute(self._data, "relationships.offers.data")
        ]

    @property
    def result_detail_ids(self) -> list[str]:
        return [
            get_nested_attribute(rd, "id")
            for rd in get_nested_attribute(
                self._data,
                "relationships.resultDetails.data",
            )
        ]


class FlightOffers(BaseResult):
    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self._data = data

    @property
    def offer_results(self) -> list[FlightOffersResult]:
        return [
            FlightOffersResult(offer_result)
            for offer_result in get_nested_attribute(self._data, "data")
        ]


class CarRentalSearchResult(BaseResult):
    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self._data = data

    @property
    def id(self) -> str:
        return get_nested_attribute(self._data, "data.id")

    @property
    def status(self) -> str:
        return get_nested_attribute(self._data, "data.attributes.status")


class CarRentalOfferResult(BaseResult):
    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self._data = data

    @property
    def offers(self) -> str:
        return get_nested_attribute(self._data, "data.0.relationships.offers")


class HotelSearchResult(BaseResult):
    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self._data = data

    @property
    def id(self) -> str:
        return get_nested_attribute(self._data, "data.id")

    @property
    def status(self) -> str:
        return get_nested_attribute(self._data, "data.attributes.status")


class HotelOfferResult(BaseResult):
    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self._data = data

    @property
    def offers(self) -> str:
        return get_nested_attribute(self._data, "data.attributes.data")

    @property
    def first_hotel_reference(self) -> str:
        return get_nested_attribute(self._data, "data.attributes.data.0.refs.0")


class HotelRoomSearchResult(BaseResult):
    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self._data = data

    @property
    def id(self) -> str:
        return get_nested_attribute(self._data, "data.id")

    @property
    def status(self) -> str:
        return get_nested_attribute(self._data, "data.attributes.status")


class HotelRoomOfferResult(BaseResult):
    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self._data = data

    @property
    def offers(self) -> str:
        return get_nested_attribute(self._data, "data.attributes.data")


class FerrySearchResult(BaseResult):
    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self._data = data

    @property
    def id(self) -> str:
        return get_nested_attribute(self._data, "data.id")

    @property
    def status(self) -> str:
        return get_nested_attribute(self._data, "data.attributes.status")


class FerryOfferResult(BaseResult):
    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self._data = data

    @property
    def offers(self) -> str:
        return get_nested_attribute(self._data, "data")


class TrainSearchResult(BaseResult):
    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self._data = data

    @property
    def id(self) -> str:
        return get_nested_attribute(self._data, "data.id")

    @property
    def status(self) -> str:
        return get_nested_attribute(self._data, "data.attributes.status")


class TrainOfferResult(BaseResult):
    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self._data = data

    @property
    def id(self) -> str:
        return get_nested_attribute(self._data, "id")

    @property
    def offer_ids(self) -> list[str]:
        return [
            get_nested_attribute(offer, "id")
            for offer in get_nested_attribute(self._data, "relationships.offers.data")
        ]

    @property
    def result_detail_ids(self) -> list[str]:
        return [
            get_nested_attribute(rd, "id")
            for rd in get_nested_attribute(
                self._data,
                "relationships.resultDetails.data",
            )
        ]


class TrainOffers(BaseResult):
    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self._data = data

    @property
    def offer_results(self) -> list[TrainOfferResult]:
        return [
            TrainOfferResult(offer_result)
            for offer_result in get_nested_attribute(self._data, "data")
        ]
