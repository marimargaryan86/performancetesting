from snowfall.project.junction.service.providers.save_a_train.v1alpha import amqp_pb2
from snowfall.stdlib import string


def offer_group_cache_key(task: amqp_pb2.SearchCriteriaTask) -> str:
    return string.to_uuid(
        b"\x00".decode().join(
            [
                task.session_token,
                *[segment.id for segment in task.segments],
                task.criteria.cabin_class,
                *[str(age) for age in task.criteria.passengers_ages],
            ],
        ),
    )
