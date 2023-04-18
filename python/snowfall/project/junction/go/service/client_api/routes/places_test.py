import httpx

from snowfall.project.junction.go import fixtures
from snowfall.project.junction.go.service.places.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import testing


class TestPlaces(object):
    async def test_places(self, client: httpx.AsyncClient) -> None:
        await testing.test_list_and_view_endpoints(
            client=client,
            url="/places",
            expected_ids=fixtures.PLACES,
        )

    async def test_place_types(self, client: httpx.AsyncClient) -> None:
        await testing.test_list_and_view_endpoints(
            client=client,
            url="/places/types",
            expected_ids=[
                protobuf.enum_value_to_slug(
                    enum_descriptor=models_pb2.Location.Type.DESCRIPTOR,
                    enum_value=place_type,
                )
                for place_type in models_pb2.Location.Type.values()
            ],
        )
