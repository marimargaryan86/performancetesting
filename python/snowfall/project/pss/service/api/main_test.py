from typing import cast
from unittest.mock import Mock

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from snowfall.project.pss.service.api.db.models.countries import Country
from snowfall.project.pss.service.api.main import _factory
from snowfall.project.pss.service.api.services.countries import CountriesService


def test_get_all_countries_returns_correct_json_response() -> None:
    mocked_countries_service = Mock()
    mocked_countries_service.get_all.return_value = [
        Country(id=1, name="fakecountry", label="fakecountrylabel", code="fakecode"),
    ]
    app_under_test: FastAPI = cast(FastAPI, _factory()())
    app_under_test.dependency_overrides[
        CountriesService
    ] = lambda: mocked_countries_service

    client = TestClient(app_under_test)
    resp = client.get("/countries")
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp_json) == 1
    assert {
        "code": "fakecode",
        "id": 1,
        "label": "fakecountrylabel",
        "name": "fakecountry",
    } in resp_json
