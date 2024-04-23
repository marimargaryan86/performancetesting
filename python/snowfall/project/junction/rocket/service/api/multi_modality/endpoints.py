import dataclasses

import grpc
import pydantic
from starlette import exceptions, responses, routing, status

from snowfall.project.junction.rocket.service.api.multi_modality import (
    models,
    repository,
)
from snowfall.project.junction.rocket.service.api.v1alpha import multi_modal_pb2
from snowfall.project.junction.rocket.service.places.v1alpha import (
    places_pb2,
    places_pb2_grpc,
)
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import (
    messages,
    routes,
)
from snowfall.stdlib.integration.starlette import models as std_models
from snowfall.stdlib.transport.amqp import protocol as amqp_producer


@dataclasses.dataclass(frozen=True)
class Suggestions:
    _repository: repository.SuggestionRepository

    async def get(self, request: messages.Request) -> responses.Response:
        suggestion = await self._repository.find_by_id(
            request.path_params["journeySuggestionId"],
        )

        if not suggestion:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return await messages.create_response(
            body=std_models.Body(
                data=models.Suggestion.from_proto(
                    suggestion,
                    request.starlette_request,
                ),
            ),
            request=request.starlette_request,
        )


@dataclasses.dataclass(frozen=True)
class SuggestionSearches:
    _repository: repository.SuggestionSearchRepository
    _places: places_pb2_grpc.PlacesServiceStub
    _producer: amqp_producer.Producer

    async def get(self, request: messages.Request) -> responses.Response:
        search = await self._repository.find_by_id(
            request.path_params["journeySuggestionSearchId"],
        )

        if not search:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return await messages.create_response(
            body=std_models.Body(
                data=models.SuggestionSearch.from_proto(
                    search,
                    request.starlette_request,
                ),
            ),
            request=request.starlette_request,
        )

    async def post(self, request: messages.Request) -> responses.Response:
        try:
            criteria = await self._to_criteria(request)
        except models.ValidationError as err:
            return err.to_response()

        search = await self._repository.create_from_criteria(criteria)
        await self._producer.publish(
            multi_modal_pb2.SuggestionSearchTask(suggestion_search_id=search.id),
            "tasks.suggestion_search",
        )

        return await messages.create_response(
            body=std_models.Body(
                data=models.SuggestionSearch.from_proto(
                    search,
                    request.starlette_request,
                ),
            ),
            request=request.starlette_request,
            status_code=status.HTTP_201_CREATED,
        )

    async def _to_criteria(
        self,
        request: messages.Request,
    ) -> multi_modal_pb2.SuggestionSearch.Criteria:
        try:
            body = models.SuggestionSearchBody.model_validate(request.body)
        except pydantic.ValidationError as err:
            raise models.ValidationError([
                std_models.Error(
                    status=str(status.HTTP_422_UNPROCESSABLE_ENTITY),
                    code=error["type"],
                    detail=error["msg"],
                    source=std_models.ErrorSourcePointer(
                        pointer="/data/attributes/{0}".format(
                            "/".join(map(str, error["loc"])),
                        ),
                    ),
                )
                for error in err.errors()
            ]) from err

        errors = []
        try:
            await self._places.GetPlace(
                places_pb2.GetPlaceRequest(id=body.origin),
            )
        except grpc.aio.AioRpcError:
            errors.append(
                std_models.Error(
                    status=str(status.HTTP_422_UNPROCESSABLE_ENTITY),
                    code="not_found",
                    detail="Place ID {0} not found".format(body.origin),
                    source=std_models.ErrorSourcePointer(
                        pointer="/data/relationships/origin/data/id",
                    ),
                ),
            )

        try:
            await self._places.GetPlace(
                places_pb2.GetPlaceRequest(id=body.destination),
            )
        except grpc.aio.AioRpcError:
            errors.append(
                std_models.Error(
                    status=str(status.HTTP_422_UNPROCESSABLE_ENTITY),
                    code="not_found",
                    detail="Place ID {0} not found".format(body.destination),
                    source=std_models.ErrorSourcePointer(
                        pointer="/data/relationships/destination/data/id",
                    ),
                ),
            )

        if errors:
            raise models.ValidationError(errors)

        return multi_modal_pb2.SuggestionSearch.Criteria(
            origin_id=body.origin,
            destination_id=body.destination,
            departure_after=protobuf.datetime_to_protobuf_datetime(
                body.departure_after,
            ),
            passengers=[
                multi_modal_pb2.SuggestionSearch.Criteria.Passenger(
                    date_of_birth=protobuf.date_to_protobuf(passenger.date_of_birth),
                )
                for passenger in body.passengers
            ],
            reseller_id=request.starlette_request.user.username,
        )


def get_routes(
    suggestions: Suggestions,
    suggestion_searches: SuggestionSearches,
) -> list[routing.Route]:
    return [
        routes.to_route(
            "/journeys/suggestions/{journeySuggestionId}",
            suggestions.get,
            name="GetJourneySuggestion",
        ),
        routes.to_route(
            "/journeys/suggestions/searches",
            suggestion_searches.post,
            methods=["POST"],
        ),
        routes.to_route(
            "/journeys/suggestions/searches/{journeySuggestionSearchId}",
            suggestion_searches.get,
            name="GetJourneySuggestionSearch",
        ),
    ]
