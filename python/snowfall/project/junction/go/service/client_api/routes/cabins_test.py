import httpx

from snowfall.project.junction.go.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import testing


class TestCabins(object):
    async def test_cabin_classes_are_found(self, client: httpx.AsyncClient) -> None:
        await testing.test_list_and_view_endpoints(
            client=client,
            url="/cabin-classes",
            expected_ids=[
                protobuf.enum_value_to_slug(
                    enum_descriptor=models_pb2.CabinClass.Type.DESCRIPTOR,
                    enum_value=cabin_class,
                )
                for cabin_class in models_pb2.CabinClass.Type.values()
            ],
        )
