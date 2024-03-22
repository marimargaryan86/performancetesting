from snowfall.project.junction.rocket.service.providers.carnect import criteria
from snowfall.stdlib import string


def generate_cache_key(search: criteria.Criteria) -> str:
    return string.to_uuid(
        "\x00".join(
            (
                str(search.origin),
                str(search.destination),
                str(search.driver_age),
                str(search.pickup_datetime),
                str(search.return_datetime),
            ),
        ),
    )
