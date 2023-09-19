import pytest

from snowfall.project.junction.plus.adapter import validation


async def test_valid_search_url_templates() -> None:
    valid_url = (
        "https://www.example.com/flight?origin={origin}&"
        "destination={destination}&day={day}&month={month}&year={year}"
    )
    validation.validate_search_url_template(valid_url)


async def test_invalid_search_url_templates() -> None:
    url_message_pairs = {
        None: "Search URL template should not be empty",
        "https://": "Missing field, must have dynamic fields",
        "https://a.com/{origin}{destination}{day}{month}{year}{extrakey}": (
            "Template is not formattable"
        ),
    }
    for url, message in url_message_pairs.items():
        with pytest.raises(ValueError, match=message):
            validation.validate_search_url_template(url)
