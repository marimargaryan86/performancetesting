from starlette import requests

from snowfall.project.junction.go.v1 import models_pb2
from snowfall.stdlib.format import protobuf


def get_cabin_class_filter(
    request: requests.Request,
) -> list[models_pb2.CabinClass.Type.ValueType]:
    cabin_classes_raw = request.scope["parsed_query_string"].get(
        "filter[groups.options.details.cabinClass][eq]",
        [],
    )

    cabin_class_enums: list[models_pb2.CabinClass.Type.ValueType] = []

    for cabin_class_id in cabin_classes_raw:
        try:
            cabin_class_enums.append(
                protobuf.slug_to_enum_value(
                    models_pb2.CabinClass.Type,
                    cabin_class_id,
                ),
            )
        except ValueError:
            cabin_class_enums.append(models_pb2.CabinClass.TYPE_UNSPECIFIED)

    return cabin_class_enums
