from dataclasses import dataclass

import pytest
from httpx import HTTPStatusError

from snowfall.project.junction.api_automation.service_objects.qa_client import (
    QaClient,
)


@dataclass(frozen=True)
class ExpectedPlaceData:
    place_id: str
    latitude: float
    longitude: float
    country_code: str
    country_name: str
    iata_code: str


@dataclass(frozen=True)
class PlaceListFilters:
    name_like: str
    type_eq: str
    iata_eq: str
    coordinates: str
    place_to_search_within: str
    page_limit: int


valid_place_filters = PlaceListFilters(
    name_like="London",
    type_eq="city",
    iata_eq="BER",
    coordinates="13.3888599,52.5170365,0",
    place_to_search_within="c6c12798-1668-5812-b611-7aa1709daee4",
    page_limit=5,
)
valid_place_filters_combination = PlaceListFilters(
    name_like="Berlin",
    type_eq="airport",
    iata_eq="LON",
    coordinates="13.49691,52.3665044,0",
    place_to_search_within="c6c12798-1668-5812-b611-7aa1709daee4",
    page_limit=3,
)
empty_places_filters_params = PlaceListFilters(
    name_like="",
    type_eq="",
    iata_eq="",
    coordinates="",
    place_to_search_within="",
    page_limit=0,
)


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_valid_place_id(qa_client: QaClient) -> None:  # noqa: WPS218
    place_id = "c6c12798-1668-5812-b611-7aa1709daee4"
    expected_data = ExpectedPlaceData(
        place_id="c6c12798-1668-5812-b611-7aa1709daee4",
        latitude=52.5170365,
        longitude=13.3888599,
        country_code="DE",
        country_name="Germany",
        iata_code="BER",
    )

    place_data = await qa_client.places.get_place_by_place_id(place_id)
    assert place_data.id == expected_data.place_id, "IDs do not match"
    assert place_data.latitude == expected_data.latitude, "Latitudes do not match"
    assert place_data.longitude == expected_data.longitude, "Longitudes do not match"
    assert (
        place_data.country_code == expected_data.country_code
    ), "Country codes do not match"
    assert (
        place_data.country_name == expected_data.country_name
    ), "Country names do not match"
    assert place_data.iata_code == expected_data.iata_code, "IATA codes do not match"


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_empty_place_id(
    qa_client: QaClient,
) -> None:
    empty_place_id = ""

    with pytest.raises(HTTPStatusError, match="Client error '400 Bad Request"):
        await qa_client.places.get_place_by_place_id(
            place_id=empty_place_id,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_invalid_place_id(
    qa_client: QaClient,
) -> None:
    invalid_place_id = "invalid-uuid"

    with pytest.raises(HTTPStatusError, match="Client error '400 Bad Request"):
        await qa_client.places.get_place_by_place_id(
            place_id=invalid_place_id,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_not_exist_place_id(
    qa_client: QaClient,
) -> None:
    not_exist_place_id = "b4a85aa0-24e7-459f-97e3-f66760348dab"

    with pytest.raises(HTTPStatusError, match="Client error '404 Not Found"):
        await qa_client.places.get_place_by_place_id(
            place_id=not_exist_place_id,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_list_name_like(
    qa_client: QaClient,
) -> None:
    place_data = await qa_client.places.get_place_list(
        name_like=valid_place_filters.name_like,
    )
    assert place_data.places[0].id, "Place data does not have an id"
    assert (
        valid_place_filters.name_like in place_data.places[0].name
    ), "{0} is not contained in {1}".format(
        valid_place_filters.name_like,
        place_data.places[0].name,
    )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_list_type_eq(
    qa_client: QaClient,
) -> None:
    place_data = await qa_client.places.get_place_list(
        type_eq=valid_place_filters.type_eq,
    )
    assert place_data.places[0].id, "Place data does not have an id"
    assert place_data.places[0].place_type == valid_place_filters.type_eq


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_list_multi_type_eq(
    qa_client: QaClient,
) -> None:
    place_data = await qa_client.places.get_place_list(
        type_eq="airport,railway-station",
    )
    assert place_data.places[0].id, "Place data does not have an id"
    assert place_data.places[0].place_type in {
        "airport",
        "railway-station",
    }, "Expected place_type to be 'airport' or 'railway-station', got {0}".format(
        place_data.places[0].place_type,
    )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_list_iata_eq(
    qa_client: QaClient,
) -> None:
    place_data = await qa_client.places.get_place_list(
        iata_eq=valid_place_filters.iata_eq,
    )
    assert place_data.places[0].id, "Place data does not have an id"
    assert place_data.places[0].iata_code == valid_place_filters.iata_eq


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_coordinates(
    qa_client: QaClient,
) -> None:
    place_data = await qa_client.places.get_place_list(
        coordinates=valid_place_filters.coordinates,
    )

    longitude, latitude, _radius = map(
        float,
        valid_place_filters.coordinates.split(","),
    )

    assert place_data.places[0].id, "Place data does not have an id"
    assert (
        place_data.places[0].latitude == latitude
    ), "Expected latitude {0}, but got {1}".format(
        latitude,
        place_data.places[0].latitude,
    )
    assert (
        place_data.places[0].longitude == longitude
    ), "Expected longitude {0}, but got {1}".format(
        longitude,
        place_data.places[0].longitude,
    )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_search_within(
    qa_client: QaClient,
) -> None:
    place_data = await qa_client.places.get_place_list(
        place_to_search_within=valid_place_filters.place_to_search_within,
    )
    assert place_data.places[0].id, "Place data does not have an id"
    assert (
        place_data.places[0].country_code == "DE"
    ), "Expected all places to have the country code 'DE', but found a country code of '{0}' in the data.".format(
        place_data.places[0].country_code,
    )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_combination_no_iata(  # noqa: WPS218
    qa_client: QaClient,
) -> None:
    place_data = await qa_client.places.get_place_list(
        name_like=valid_place_filters_combination.name_like,
        type_eq=valid_place_filters_combination.type_eq,
        coordinates=valid_place_filters_combination.coordinates,
    )
    assert place_data.places[0].id, "Place data does not have an id"
    assert (
        valid_place_filters_combination.name_like in place_data.places[0].name
    ), "{0} is not contained in {1}".format(
        valid_place_filters_combination.name_like,
        place_data.places[0].name,
    )
    assert place_data.places[0].place_type == valid_place_filters_combination.type_eq
    longitude, latitude, _radius = map(
        float,
        valid_place_filters_combination.coordinates.split(","),
    )

    assert place_data.places[0].id, "Place data does not have an id"
    assert (
        place_data.places[0].latitude == latitude
    ), "Expected latitude {0}, but got {1}".format(
        latitude,
        place_data.places[0].latitude,
    )
    assert (
        place_data.places[0].longitude == longitude
    ), "Expected longitude {0}, but got {1}".format(
        longitude,
        place_data.places[0].longitude,
    )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_combination_with_iata(  # noqa: WPS218
    qa_client: QaClient,
) -> None:
    expected_data = ExpectedPlaceData(
        place_id="6da9e96b-5f05-5034-b5d5-993086525f0d",
        latitude=51.5073219,
        longitude=-0.1276474,
        country_code="GB",
        country_name="United Kingdom",
        iata_code="LON",
    )
    place_data = await qa_client.places.get_place_list(
        name_like=valid_place_filters_combination.name_like,
        type_eq=valid_place_filters_combination.type_eq,
        iata_eq=valid_place_filters_combination.iata_eq,
    )
    assert place_data.places[0].id, "Place data does not have an id"
    assert place_data.places[0].country_code == expected_data.country_code
    assert place_data.places[0].country_name == expected_data.country_name
    assert place_data.places[0].iata_code == expected_data.iata_code

    assert (
        place_data.places[0].latitude == expected_data.latitude
    ), "Expected latitude {0}, but got {1}".format(
        expected_data.latitude,
        place_data.places[0].latitude,
    )
    assert (
        place_data.places[0].longitude == expected_data.longitude
    ), "Expected longitude {0}, but got {1}".format(
        expected_data.longitude,
        place_data.places[0].longitude,
    )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_list_empty_name(
    qa_client: QaClient,
) -> None:
    with pytest.raises(HTTPStatusError, match="Client error '400 Bad Request"):
        await qa_client.places.get_place_list(
            name_like=empty_places_filters_params.name_like,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_list_empty_iata_eq(
    qa_client: QaClient,
) -> None:
    with pytest.raises(HTTPStatusError, match="Client error '400 Bad Request"):
        await qa_client.places.get_place_list(
            iata_eq=empty_places_filters_params.iata_eq,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_list_empty_type_eq(
    qa_client: QaClient,
) -> None:
    with pytest.raises(HTTPStatusError, match="Client error '400 Bad Request"):
        await qa_client.places.get_place_list(
            type_eq=empty_places_filters_params.type_eq,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_list_empty_coordinates(
    qa_client: QaClient,
) -> None:
    with pytest.raises(HTTPStatusError, match="Client error '400 Bad Request"):
        await qa_client.places.get_place_list(
            coordinates=empty_places_filters_params.coordinates,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_list_empty_search_within(
    qa_client: QaClient,
) -> None:
    with pytest.raises(HTTPStatusError, match="Client error '400 Bad Request"):
        await qa_client.places.get_place_list(
            place_to_search_within=empty_places_filters_params.place_to_search_within,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_list_short_name(
    qa_client: QaClient,
) -> None:
    with pytest.raises(HTTPStatusError, match="Client error '400 Bad Request"):
        await qa_client.places.get_place_list(
            name_like="Lo",
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_list_name_like_no_iata(
    qa_client: QaClient,
) -> None:
    place_data = await qa_client.places.get_place_list(
        name_like="Vienna",
    )
    assert place_data.places[0].id, "Place data does not have an id"
    assert place_data.places[0].name == "Vienna", "The response value is not 'Vienna'"


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_list_pagination(
    qa_client: QaClient,
) -> None:
    place_data = await qa_client.places.get_place_list(
        name_like=valid_place_filters.name_like,
        page_limit=valid_place_filters.page_limit,
    )
    assert place_data.places[0].id, "Place data does not have an id"
    assert (
        len(place_data.places) == valid_place_filters.page_limit
    ), "Expected {0} items in the first response, found {1}".format(
        valid_place_filters.page_limit,
        len(place_data.places),
    )

    next_link = place_data.next_link
    next_page_data = await qa_client.places.get_place_by_next_link(url=next_link)
    assert next_page_data.places[0].id, "Next page data does not have an id"
    assert (
        len(next_page_data.places) == valid_place_filters.page_limit
    ), "Expected {0} items in the second response, found {1}".format(
        valid_place_filters.page_limit,
        len(next_page_data.places),
    )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_list_not_default_limit(
    qa_client: QaClient,
) -> None:
    place_data = await qa_client.places.get_place_list(
        page_limit=valid_place_filters_combination.page_limit,
    )
    assert place_data.places[0].id, "Place data does not have an id"
    assert (
        len(place_data.places) == valid_place_filters_combination.page_limit
    ), "Expected {0} items in the first response, found {1}".format(
        valid_place_filters_combination.page_limit,
        len(place_data.places),
    )

    next_link = place_data.next_link
    next_page_data = await qa_client.places.get_place_by_next_link(url=next_link)
    assert next_page_data.places[0].id, "Next page data does not have an id"
    assert (
        len(next_page_data.places) == valid_place_filters_combination.page_limit
    ), "Expected {0} items in the second response, found {1}".format(
        valid_place_filters_combination.page_limit,
        len(next_page_data.places),
    )
