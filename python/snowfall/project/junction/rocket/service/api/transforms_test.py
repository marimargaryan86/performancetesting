from datetime import date

import freezegun

from snowfall.project.junction.rocket.service.api.transforms import (
    AirSearchRequestTransformer,
)


@freezegun.freeze_time("2024-03-20")
def test_transform_basic_request() -> None:
    request = {
        "data": {
            "type": "searches",
            "attributes": {
                "date": date(2024, 1, 1),
                "origin": "JFK",
                "destination": "LAX",
                "passengers": [
                    {"date_of_birth": date(1980, 1, 1)},
                    {"date_of_birth": date(2010, 1, 1)},
                    {"date_of_birth": date(2022, 1, 1)},
                ],
            },
        },
    }

    transformed = AirSearchRequestTransformer().transform(request)

    assert transformed.model_dump(exclude_none=True) == {
        "ods": [
            {
                "arrival_airport": "LAX",
                "departure_airport": "JFK",
                "departure_date": date(2024, 1, 1),
            },
        ],
        "user_ids": [-10, -11, -21],
    }
