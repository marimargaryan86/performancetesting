from collections.abc import AsyncIterable, Mapping, Sequence
from typing import Any
from unittest import mock

import pytest

from snowfall.project.junction.rocket.service.places import constants
from snowfall.project.junction.rocket.service.places.places import (
    cities_to_places,
    get_provider_places,
    osm_nodes_to_places,
    resolve_city_search_capabilities,
    resolve_osm_properties,
    tag_all_non_cities_against_a_city,
    validate_name,
)
from snowfall.project.junction.rocket.service.places.typing import ProviderTypedDict
from snowfall.project.junction.rocket.service.places.v1alpha import models_pb2


class TestPlaces:
    @pytest.mark.parametrize(
        ("input_node", "expected_output"),
        [
            ({}, None),
            ({"properties": {}}, None),
            ({"properties": {"name:en": "English Name"}}, "English Name"),
            ({"properties": {"int_name": "International Name"}}, "International Name"),
            ({"properties": {"name": "Name"}}, "Name"),
            ({"properties": {"alt_name": "Alternate Name"}}, "Alternate Name"),
            (
                {
                    "properties": {
                        "name:en": "",
                        "int_name": "",
                        "name": "",
                        "alt_name": "",
                    },
                },
                None,
            ),
            (
                {
                    "properties": {
                        "name:en": None,
                        "int_name": None,
                        "name": None,
                        "alt_name": None,
                    },
                },
                None,
            ),
        ],
    )
    def test_validate_name(
        self,
        input_node: Mapping[str, Any],
        expected_output: str | None,
    ) -> None:
        assert validate_name(input_node) == expected_output

    @pytest.mark.parametrize(
        ("input_node", "expected_output"),
        [
            ({}, {"iata": None, "type": models_pb2.Type.TYPE_UNSPECIFIED}),
            (
                {"properties": {"iata": "LHR"}},
                {"iata": None, "type": models_pb2.Type.TYPE_UNSPECIFIED},
            ),
            (
                {"properties": {"aeroway": "aerodrome"}},
                {"iata": None, "type": models_pb2.Type.TYPE_UNSPECIFIED},
            ),
            (
                {"properties": {"aeroway": "aerodrome", "iata": "1243"}},
                {"iata": None, "type": models_pb2.Type.TYPE_UNSPECIFIED},
            ),
            (
                {"properties": {"aeroway": "aerodrome", "iata": "LHR"}},
                {"iata": "LHR", "type": models_pb2.Type.TYPE_AIRPORT},
            ),
            (
                {"properties": {"railway": "station"}},
                {"iata": None, "type": models_pb2.Type.TYPE_RAILWAY_STATION},
            ),
            (
                {"properties": {"amenity": "ferry_terminal"}},
                {"iata": None, "type": models_pb2.Type.TYPE_FERRY_PORT},
            ),
        ],
    )
    def test_resolve_osm_properties_correctly_assigns_type_and_iata(
        self,
        input_node: Mapping[str, Any],
        expected_output: Mapping[str, Any],
    ) -> None:
        assert resolve_osm_properties(input_node) == expected_output

    def test_get_provider_places_returns_nothing_if_no_vertical_match(self) -> None:
        provider_jsons: ProviderTypedDict = {
            models_pb2.TYPE_RAILWAY_STATION: {"an-id": []},
            models_pb2.TYPE_AIRPORT: {"an-id-1": []},
        }

        assert get_provider_places(
            node={},
            vertical_type=models_pb2.Type.TYPE_FERRY_PORT,
            provider_jsons=provider_jsons,
            iata=None,
        ) == {
            models_pb2.TYPE_RAILWAY_STATION: [],
            models_pb2.TYPE_FERRY_PORT: [],
            models_pb2.TYPE_AIRPORT: [],
        }

    @mock.patch(
        "snowfall.project.junction.rocket.service.places.handlers.place_within_radius",
    )
    def test_get_provider_places_returns_result_if_provider_place_in_radius(
        self,
        mock_place_within_radius: mock.Mock,
    ) -> None:
        mock_place_within_radius.return_value = "a-provider-id"
        node = {"geometry": {"coordinates": [0, 1]}}
        provider_json: ProviderTypedDict = {
            models_pb2.TYPE_RAILWAY_STATION: {"an-id": [], "an-id-1": []},
            models_pb2.TYPE_AIRPORT: {"an-id-2": []},
        }
        assert get_provider_places(
            node=node,
            vertical_type=models_pb2.TYPE_RAILWAY_STATION,
            provider_jsons=provider_json,
            iata=None,
        ) == {
            models_pb2.TYPE_RAILWAY_STATION: [
                models_pb2.ProviderPlaceId(
                    snowfall_provider_id="an-id",
                    provider_place_id="a-provider-id",
                ),
                models_pb2.ProviderPlaceId(
                    snowfall_provider_id="an-id-1",
                    provider_place_id="a-provider-id",
                ),
            ],
            models_pb2.TYPE_FERRY_PORT: [],
            models_pb2.TYPE_AIRPORT: [],
        }

    @mock.patch(
        "snowfall.project.junction.rocket.service.places.handlers.place_within_radius",
    )
    def test_get_provider_places_returns_result_if_iata_present(
        self,
        mock_place_within_radius: mock.Mock,
    ) -> None:
        mock_place_within_radius.return_value = "a-provider-id"
        node = {"geometry": {"coordinates": [0, 1]}}
        provider_json: ProviderTypedDict = {
            models_pb2.TYPE_RAILWAY_STATION: {"an-id": [], "an-id-1": []},
            models_pb2.TYPE_FERRY_PORT: {"an-id-2": []},
        }
        assert get_provider_places(
            node=node,
            vertical_type=models_pb2.TYPE_RAILWAY_STATION,
            provider_jsons=provider_json,
            iata="LHR",
        ) == {
            models_pb2.TYPE_RAILWAY_STATION: [
                models_pb2.ProviderPlaceId(
                    snowfall_provider_id="an-id",
                    provider_place_id="a-provider-id",
                ),
                models_pb2.ProviderPlaceId(
                    snowfall_provider_id="an-id-1",
                    provider_place_id="a-provider-id",
                ),
            ],
            models_pb2.TYPE_FERRY_PORT: [],
            models_pb2.TYPE_AIRPORT: [
                models_pb2.ProviderPlaceId(
                    snowfall_provider_id=constants.IATA_ID,
                    provider_place_id="LHR",
                ),
            ],
        }

    @mock.patch(
        "snowfall.project.junction.rocket.service.places.handlers.place_within_radius",
    )
    def test_get_provider_places_returns_empty_result_if_provider_place_not_in_radius(
        self,
        mock_place_within_radius: mock.Mock,
    ) -> None:
        mock_place_within_radius.return_value = None
        node = {"geometry": {"coordinates": [0, 1]}}
        provider_json: ProviderTypedDict = {
            models_pb2.TYPE_RAILWAY_STATION: {"an-id": []},
            models_pb2.TYPE_AIRPORT: {"an-id-1": []},
        }
        assert get_provider_places(
            node=node,
            vertical_type=models_pb2.TYPE_RAILWAY_STATION,
            provider_jsons=provider_json,
            iata=None,
        ) == {
            models_pb2.TYPE_RAILWAY_STATION: [],
            models_pb2.TYPE_FERRY_PORT: [],
            models_pb2.TYPE_AIRPORT: [],
        }

    async def test_osm_nodes_to_places_yields_empty_if_invalid_name(self) -> None:
        places = [
            place
            async for place in osm_nodes_to_places(
                osm_nodes=[{"id": "id"}],
                provider_jsons={},
                geocoding=mock.Mock(),
                country_codes_to_countries={},
            )
        ]
        assert not places

    async def test_osm_nodes_to_places_yields_empty_if_node_has_no_type(self) -> None:
        places = [
            place
            async for place in osm_nodes_to_places(
                osm_nodes=[{"id": "id", "properties": {"name": "hello"}}],
                provider_jsons={},
                geocoding=mock.Mock(),
                country_codes_to_countries={},
            )
        ]
        assert not places

    @mock.patch(
        "snowfall.project.junction.rocket.service.places.places.get_provider_places",
    )
    async def test_osm_nodes_to_places_yields_empty_if_no_places_matched(
        self,
        mock_provider_places: mock.Mock,
    ) -> None:
        mock_provider_places.return_value = {
            models_pb2.TYPE_RAILWAY_STATION: [],
            models_pb2.TYPE_FERRY_PORT: [],
            models_pb2.TYPE_AIRPORT: [],
        }
        places = [
            place
            async for place in osm_nodes_to_places(
                osm_nodes=[
                    {
                        "id": "id",
                        "properties": {"name": "hello", "railway": "station"},
                    },
                ],
                provider_jsons={},
                geocoding=mock.Mock(),
                country_codes_to_countries={},
            )
        ]
        assert not places

    @mock.patch(
        "snowfall.project.junction.rocket.service.places.places.get_country_code_and_timezone",
    )
    @mock.patch(
        "snowfall.project.junction.rocket.service.places.places.get_provider_places",
    )
    async def test_osm_nodes_yields_place_when_successfully_matched_to_provider(
        self,
        mock_provider_places: mock.Mock,
        mock_get_country_code_and_timezone: mock.Mock,
    ) -> None:
        mock_provider_places.return_value = {
            models_pb2.TYPE_RAILWAY_STATION: [],
            models_pb2.TYPE_FERRY_PORT: [],
            models_pb2.TYPE_AIRPORT: [
                models_pb2.ProviderPlaceId(
                    snowfall_provider_id="an-id",
                    provider_place_id="123",
                ),
            ],
        }
        mock_get_country_code_and_timezone.return_value = (
            "UK",
            "Europe/London",
        )

        places = [
            place
            async for place in osm_nodes_to_places(
                osm_nodes=[
                    {
                        "id": "id",
                        "properties": {
                            "name": "hello",
                            "aeroway": "aerodrome",
                            "iata": "123",
                        },
                        "geometry": {"coordinates": [0, 0]},
                    },
                ],
                provider_jsons={},
                geocoding=mock.Mock(),
                country_codes_to_countries={"UK": "United Kingdom"},
            )
        ]
        assert places

    async def mock_iterator(
        self,
        rows: Sequence[Mapping[str, Any]],
    ) -> AsyncIterable[Mapping[str, Any]]:
        for row in rows:
            yield row

    async def test_cities_to_places_yields_empty_if_no_name_for_city(self) -> None:
        rows = [{"name": ""}]
        places = [
            place
            async for place in cities_to_places(
                cities=self.mock_iterator(rows),
                places_repository=mock.Mock(),
                geocoding=mock.Mock(),
                country_codes_to_countries=mock.Mock(),
            )
        ]
        assert not places

    async def test_cities_to_places_yields_empty_if_no_contained_places(self) -> None:
        rows = [{"name": "A City", "latitude": 0, "longitude": 0}]

        mock_repository = mock.AsyncMock()

        places = [
            place
            async for place in cities_to_places(
                cities=self.mock_iterator(rows),
                places_repository=mock_repository,
                geocoding=mock.Mock(),
                country_codes_to_countries=mock.Mock(),
            )
        ]
        assert not places

    @mock.patch(
        "snowfall.project.junction.rocket.service.places.places.get_country_code_and_timezone",
    )
    async def test_cities_to_places_yields_place_when_it_contains_places(
        self,
        mock_get_country_code_and_timezone: mock.Mock,
    ) -> None:
        rows = [{"id": "an-id", "name": "A City", "latitude": 0, "longitude": 0}]
        mock_get_country_code_and_timezone.return_value = (
            "UK",
            "Europe/London",
        )

        async def place_yield() -> AsyncIterable[models_pb2.Place]:  # noqa: WPS430
            yield models_pb2.Place(
                id="An ID",
                type=models_pb2.TYPE_AIRPORT,
                name="A Name",
            )

        mock_repository = mock.AsyncMock()
        mock_repository.find_within_radius.return_value = place_yield()

        places = [
            place
            async for place in cities_to_places(
                cities=self.mock_iterator(rows),
                places_repository=mock_repository,
                geocoding=mock.Mock(),
                country_codes_to_countries={"UK": "United Kingdom"},
            )
        ]
        assert places

    async def mock_find_by_types(
        self,
        places: Sequence[models_pb2.Place],
    ) -> AsyncIterable[models_pb2.Place]:
        for place in places:
            yield place

    async def test_tag_all_non_cities_against_a_city_doesnt_update_if_no_close_city(
        self,
    ) -> None:
        mock_repository = mock.AsyncMock()
        mock_closest_cities_results = mock.AsyncMock()
        mock_repository.find_by_types.return_value = self.mock_find_by_types(
            places=[models_pb2.Place()],
        )
        mock_repository.find_within_radius.return_value = mock_closest_cities_results
        mock_closest_cities_results.take.side_effect = StopAsyncIteration()

        await tag_all_non_cities_against_a_city(places_repository=mock_repository)

        mock_repository.update_city.assert_not_called()

    async def test_tag_all_non_cities_against_a_city_updates_if_city_close(
        self,
    ) -> None:
        close_city = models_pb2.Place(
            id="an-id",
            name="a name",
            type=models_pb2.TYPE_CITY,
        )
        mock_repository = mock.AsyncMock()
        mock_closest_cities_results = mock.AsyncMock()
        mock_repository.find_by_types.return_value = self.mock_find_by_types(
            places=[models_pb2.Place(id="an-id")],
        )
        mock_repository.find_within_radius.return_value = mock_closest_cities_results
        mock_closest_cities_results.take.return_value = close_city

        await tag_all_non_cities_against_a_city(mock_repository)

        mock_repository.update_city.assert_called_once_with(
            id_="an-id",
            city=models_pb2.PlaceIdentifier(
                id=close_city.id,
                name=close_city.name,
                type=models_pb2.TYPE_CITY,
            ),
        )

    @pytest.mark.parametrize(
        ("input_city", "expected_output"),
        [
            (
                {
                    "id": "an-id",
                    "name": "a name",
                    "longitude": 0,
                    "latitude": "0",
                    "iata": "",
                    "benerail_station_id": "",
                },
                models_pb2.ProviderMappings(rail=None, air=None, ferry=None),
            ),
            (
                {
                    "id": "an-id",
                    "name": "a name",
                    "longitude": 0,
                    "latitude": "0",
                },
                models_pb2.ProviderMappings(rail=None, air=None, ferry=None),
            ),
        ],
    )
    async def test_resolve_city_search_capabilities_returns_empty_when_none_found(
        self,
        input_city: Mapping[str, str],
        expected_output: models_pb2.ProviderMappings,
    ) -> None:
        assert resolve_city_search_capabilities(city=input_city) == expected_output

    @pytest.mark.parametrize(
        ("input_city", "expected_output"),
        [
            (
                {
                    "id": "an-id",
                    "name": "a name",
                    "longitude": 0,
                    "latitude": "0",
                    "iata": "LHR",
                    "benerail_station_id": "benerail-id",
                },
                models_pb2.ProviderMappings(
                    rail=[
                        models_pb2.ProviderPlaceId(
                            snowfall_provider_id=constants.BENERAIL_ID,
                            provider_place_id="benerail-id",
                        ),
                    ],
                    air=[
                        models_pb2.ProviderPlaceId(
                            snowfall_provider_id=constants.IATA_ID,
                            provider_place_id="LHR",
                        ),
                    ],
                    ferry=None,
                ),
            ),
            (
                {
                    "id": "an-id",
                    "name": "a name",
                    "longitude": 0,
                    "latitude": "0",
                    "iata": "LHR",
                },
                models_pb2.ProviderMappings(
                    rail=None,
                    air=[
                        models_pb2.ProviderPlaceId(
                            snowfall_provider_id=constants.IATA_ID,
                            provider_place_id="LHR",
                        ),
                    ],
                    ferry=None,
                ),
            ),
            (
                {
                    "id": "an-id",
                    "name": "a name",
                    "longitude": 0,
                    "latitude": "0",
                    "benerail_station_id": "benerail-id",
                },
                models_pb2.ProviderMappings(
                    rail=[
                        models_pb2.ProviderPlaceId(
                            snowfall_provider_id=constants.BENERAIL_ID,
                            provider_place_id="benerail-id",
                        ),
                    ],
                    air=None,
                    ferry=None,
                ),
            ),
        ],
    )
    async def test_resolve_city_search_capabilities_returns_capabilities_when_found(
        self,
        input_city: Mapping[str, str],
        expected_output: models_pb2.ProviderMappings,
    ) -> None:
        assert resolve_city_search_capabilities(city=input_city) == expected_output
