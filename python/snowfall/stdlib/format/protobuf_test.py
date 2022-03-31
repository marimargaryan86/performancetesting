from snowfall.common.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf


def test_enum_value_to_name() -> None:
    assert (
        protobuf.enum_value_to_slug(
            models_pb2.Schedule.Type.DESCRIPTOR,
            models_pb2.Schedule.TYPE_AIR,
        )
        == "air"
    )


def test_enum_name_to_value() -> None:
    assert (
        protobuf.slug_to_enum_value(
            models_pb2.Schedule.Type.DESCRIPTOR,
            "air",
        )
        == models_pb2.Schedule.TYPE_AIR
    )
