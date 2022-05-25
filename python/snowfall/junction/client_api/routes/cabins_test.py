from starlette import testclient

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.client_api.routes import conftest
from snowfall.stdlib.format import protobuf


class TestCabins(object):
    def test_cabin_classes_are_found(self, client: testclient.TestClient) -> None:
        conftest.test_list_and_view_endpoints(
            client=client,
            url="/cabin-classes",
            expected_ids=[
                protobuf.enum_value_to_slug(
                    descriptor=models_pb2.CabinClass.Type.DESCRIPTOR,
                    enum_value=cabin_class,
                )
                for cabin_class in models_pb2.CabinClass.Type.values()
            ],
        )
