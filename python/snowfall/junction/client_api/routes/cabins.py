from starlette import endpoints, exceptions, requests, responses, status

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.client_api import resources
from snowfall.stdlib import sequence
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models, pagination_helpers


class Cabin(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
    ) -> responses.Response:
        cabin_class_id = request.path_params["cabinClassId"]

        try:
            cabin_class = protobuf.slug_to_enum_value(
                models_pb2.CabinClass.Type.DESCRIPTOR,
                cabin_class_id,
            )
        except KeyError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        return models.JsonApiResponse(
            models.Body(
                data=resources.CabinClassResource.from_proto(
                    cabin_class,  # type: ignore
                    request,
                ),
            ),
        )


class Cabins(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        sequence_page = sequence.paginate(
            sequence=models_pb2.CabinClass.Type.values(),
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.CabinClassResource.from_proto(
                        cabin_class,
                        request,
                    )
                    for cabin_class in sequence_page.sequence
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("ListCabinClasses"),
                    sequence_page.cursor,
                    pagination,
                ),
            ),
        )
