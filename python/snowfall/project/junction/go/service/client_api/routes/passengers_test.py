import httpx

from snowfall.project.junction.go.service.orders.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import testing


class TestPassengers(object):
    async def test_passenger_genders_are_found(self, client: httpx.AsyncClient) -> None:
        await testing.test_list_and_view_endpoints(
            client=client,
            url="/passengers/genders",
            expected_ids=[
                protobuf.enum_value_to_slug(
                    enum_descriptor=models_pb2.Passenger.Gender.DESCRIPTOR,
                    enum_value=passenger_gender,
                )
                for passenger_gender in models_pb2.Passenger.Gender.values()
            ],
        )

    async def test_passenger_titles_are_found(self, client: httpx.AsyncClient) -> None:
        await testing.test_list_and_view_endpoints(
            client=client,
            url="/passengers/titles",
            expected_ids=[
                protobuf.enum_value_to_slug(
                    enum_descriptor=models_pb2.Passenger.Title.DESCRIPTOR,
                    enum_value=passenger_title,
                )
                for passenger_title in models_pb2.Passenger.Title.values()
            ],
        )
