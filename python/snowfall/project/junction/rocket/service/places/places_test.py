from collections.abc import Mapping
from typing import Any
from unittest import mock

import pytest

from snowfall.project.junction.rocket.service.places import constants
from snowfall.project.junction.rocket.service.places.places import (
    get_provider_places,
    osm_nodes_to_places,
    resolve_osm_properties,
    validate_name,
)
from snowfall.project.junction.rocket.service.places.typing import ProviderTypedDict
from snowfall.project.junction.rocket.service.places.v1alpha import models_pb2


class TestPlaces(object):
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

    def test_get_provider_places_returns_result_if_provider_place_in_radius(
        self,
    ) -> None:
        with mock.patch(
            "snowfall.project.junction.rocket.service.places.handlers.place_within_radius",
        ) as mock_place_within_radius:
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

    def test_get_provider_places_returns_result_if_iata_present(self) -> None:
        with mock.patch(
            "snowfall.project.junction.rocket.service.places.handlers.place_within_radius",
        ) as mock_place_within_radius:
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

    def test_get_provider_places_returns_empty_result_if_provider_place_not_in_radius(
        self,
    ) -> None:
        with mock.patch(
            "snowfall.project.junction.rocket.service.places.handlers.place_within_radius",
        ) as mock_place_within_radius:
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

    async def test_osm_nodes_to_places_yields_empty_if_no_places_matched(self) -> None:
        with mock.patch(
            "snowfall.project.junction.rocket.service.places.places.get_provider_places",
        ) as mock_provider_places:
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

    async def test_osm_nodes_yields_place_when_successfully_matched_to_provider(
        self,
    ) -> None:
        with mock.patch(
            "snowfall.project.junction.rocket.service.places.places.get_provider_places",
        ) as mock_provider_places:
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

            with mock.patch(
                "snowfall.project.junction.rocket.service.places.places.get_country_code_and_timezone",
            ) as mock_get_country_code_and_timezone:
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
