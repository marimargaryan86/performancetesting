from starlette import testclient

from snowfall.junction.client_api.routes import conftest
from snowfall.junction.orders.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf


class TestPassengers(object):
    def test_passenger_genders_are_found(self, client: testclient.TestClient) -> None:
        conftest.test_list_and_view_endpoints(
            client=client,
            url="/passengers/genders",
            expected_ids=[
                protobuf.enum_value_to_slug(
                    descriptor=models_pb2.Passenger.Gender.DESCRIPTOR,
                    enum_value=passenger_gender,
                )
                for passenger_gender in models_pb2.Passenger.Gender.values()
            ],
        )

    def test_passenger_titles_are_found(self, client: testclient.TestClient) -> None:
        conftest.test_list_and_view_endpoints(
            client=client,
            url="/passengers/titles",
            expected_ids=[
                protobuf.enum_value_to_slug(
                    descriptor=models_pb2.Passenger.Title.DESCRIPTOR,
                    enum_value=passenger_title,
                )
                for passenger_title in models_pb2.Passenger.Title.values()
            ],
        )
