from snowfall.project.junction.service.providers.carnect.v1 import amqp_pb2
from snowfall.stdlib import string


def generate_cache_key(
    search_criteria: amqp_pb2.Criteria,
) -> str:
    return string.to_uuid(
        "\x00".join(
            (
                str(search_criteria.origin),
                str(search_criteria.destination),
                str(search_criteria.passengers_count),
                str(search_criteria.pick_up_datetime),
                str(search_criteria.return_datetime),
            ),
        ),
    )
