import pytest

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.client_api.transformers import trip_ids_to_segments


@pytest.mark.parametrize(
    "segment,stops,expected",
    [
        (
            models_pb2.SegmentReference(
                origin_stop_id="B",
                destination_stop_id="D",
            ),
            [
                models_pb2.Stop(
                    id="D",
                    order=3,
                ),
                models_pb2.Stop(
                    id="B",
                    order=1,
                ),
                models_pb2.Stop(
                    id="A",
                    order=0,
                ),
                models_pb2.Stop(
                    id="F",
                    order=4,
                ),
                models_pb2.Stop(
                    id="C",
                    order=2,
                ),
            ],
            ["B", "C", "D"],
        ),
    ],
)
def test_correct_stops_are_returned(
    segment: models_pb2.SegmentReference,
    stops: list[models_pb2.Stop],
    expected: list[str],
) -> None:
    filtered_stops = trip_ids_to_segments.filter_stops_in_segment_reference(
        segment=segment,
        stops=stops,
    )
    assert expected == [stop.id for stop in filtered_stops]
