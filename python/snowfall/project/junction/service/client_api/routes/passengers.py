from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.service.client_api import resources
from snowfall.project.junction.service.orders.v1alpha import models_pb2
from snowfall.stdlib import sequence
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models, pagination_helpers


class PassengerGender(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
    ) -> responses.Response:
        passenger_gender_id = request.path_params["passengerGenderId"]
        try:
            passenger_gender = protobuf.slug_to_enum_value(
                models_pb2.Passenger.Gender.DESCRIPTOR,
                passenger_gender_id,
            )
        except KeyError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        return models.JsonApiResponse(
            models.Body(
                data=resources.PassengerGenderResource.from_proto(
                    passenger_gender,  # type: ignore[arg-type]
                    request,
                ),
            ),
        )


class PassengerGenders(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        sequence_page = sequence.paginate(
            sequence=models_pb2.Passenger.Gender.values(),
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.PassengerGenderResource.from_proto(
                        passenger_gender,
                        request,
                    )
                    for passenger_gender in sequence_page.sequence
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("ListPassengerGenders"),
                    sequence_page.cursor,
                    pagination,
                ),
            ),
        )


class PassengerTitle(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
    ) -> responses.Response:
        passenger_title_id = request.path_params["passengerTitleId"]
        try:
            passenger_title = protobuf.slug_to_enum_value(
                models_pb2.Passenger.Title.DESCRIPTOR,
                passenger_title_id,
            )
        except KeyError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        return models.JsonApiResponse(
            models.Body(
                data=resources.PassengerTitleResource.from_proto(
                    passenger_title,  # type: ignore[arg-type]
                    request,
                ),
            ),
        )


class PassengerTitles(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        sequence_page = sequence.paginate(
            sequence=models_pb2.Passenger.Title.values(),
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.PassengerTitleResource.from_proto(
                        passenger_title,
                        request,
                    )
                    for passenger_title in sequence_page.sequence
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("ListPassengerTitles"),
                    sequence_page.cursor,
                    pagination,
                ),
            ),
        )
