from snowfall.project.junction.service.providers.direct_ferries.v1alpha import amqp_pb2
from snowfall.stdlib import string


def offer_group_cache_key(task: amqp_pb2.SearchCriteriaTask) -> str:
    return string.to_uuid(
        b"\x00".decode().join(
            [
                task.session_token,
                *[segment.id for segment in task.segments],
                *[str(age) for age in sorted(task.criteria.passengers_ages)],
            ],
        ),
    )
