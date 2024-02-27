import pathlib

import orjson
from pytest_mock import MockerFixture

from snowfall.project.junction.service.providers.ask2go.stations import dump_stations


async def test_sets_europe_paris(tmp_path: pathlib.Path, mocker: MockerFixture) -> None:
    geocoder = mocker.Mock()
    geocoder.TimeZoneLookup = mocker.AsyncMock()
    time_zone = mocker.Mock()
    time_zone.time_zone.id = "Europe/Paris"
    geocoder.TimeZoneLookup.return_value = time_zone
    response = mocker.Mock()
    response.json.return_value = [
        {
            "code": "PAR",
            "name": "Paris",
            "longtitude": 10,
            "latitude": 20,
            "isEnabled": True,
            "country": "FR",
            "railname": "name",
        },
    ]
    ask2go_client = mocker.AsyncMock()
    ask2go_client.get_train_stations.return_value = response
    ask2go_json = tmp_path / "ask2go.json"
    mocker.patch(
        "snowfall.stdlib.persistence.filesystem.resource_path",
        return_value=str(ask2go_json),
    )

    await dump_stations(geocoder, ask2go_client, str(ask2go_json))

    data = orjson.loads(ask2go_json.read_text("locale"))

    assert data == [
        {
            "identifier": "PAR",
            "longitude": 10,
            "latitude": 20,
            "timezone": "Europe/Paris",
            "name": "Paris",
            "iata_country_code": "FR",
            "is_enabled": True,
            "railname": "name",
        },
    ]
