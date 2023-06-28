from collections import OrderedDict
from typing import Any

import pytest

from snowfall.stdlib.logging import filtering


def test_secret_keys_are_filtered() -> None:  # noqa: WPS218
    event_dict: dict[str, Any] = {
        "perfectly_fine": "foobar",
        "password": "foobar",
        "foo": {
            "bar": {
                "password": "foobar",
            },
        },
        "baz": [
            {
                "qux": {
                    "password": "foobar",
                },
            },
        ],
        "quux": [
            [
                {
                    "password": "foobar",
                },
            ],
        ],
        "quz": [
            OrderedDict(password="foobar"),
        ],
        "secret": {
            "info": "foobar",
        },
    }
    filtered_dict = filtering.filter_secrets_dict(event_dict)
    assert filtered_dict["perfectly_fine"] == "foobar"
    assert filtered_dict["password"] == filtering.FILTERED_WORD
    assert filtered_dict["foo"]["bar"]["password"] == filtering.FILTERED_WORD
    assert filtered_dict["baz"][0]["qux"]["password"] == filtering.FILTERED_WORD
    assert filtered_dict["quux"][0][0]["password"] == filtering.FILTERED_WORD
    assert filtered_dict["quz"][0]["password"] == filtering.FILTERED_WORD
    assert filtered_dict["secret"] == filtering.FILTERED_WORD


@pytest.mark.parametrize(
    "test_input",
    [
        "password",
        "passwd",
        "pwd",
        "secret",
        "api_key",
        "apikey",
        "apiKey",
        "APIKEY",
        "credentials",
    ],
)
def test_secrets_are_detected(test_input: str) -> None:
    assert filtering.is_key_secret(test_input)


@pytest.mark.parametrize(
    "test_input",
    [
        "foobar",
        "error",
        "arons",
        6,
    ],
)
def test_non_secrets_are_not_detected(test_input: str) -> None:
    assert not filtering.is_key_secret(test_input)
