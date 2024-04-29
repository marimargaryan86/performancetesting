import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.fti.service.bigxtra_api import repository
from snowfall.project.fti.service.bigxtra_api.routes import models
from snowfall.project.fti.service.bigxtra_api.schemas import SchemaGenerator


class Places(endpoints.HTTPEndpoint):
    @SchemaGenerator.schema(
        response_body=models.PlacesModel,
        query_parameters=models.PlacesQueryParams,
        description="Use this endpoint to list Places",
        summary="List places",
    )
    async def get(
        self,
        request: requests.Request,
        fti_repository: repository.Repository = lagom.injectable,
    ) -> responses.JSONResponse:
        query_params = models.PlacesQueryParams.model_validate(request.query_params)
        places = await fti_repository.find_places(query_params.destination)
        return responses.JSONResponse(
            content=models.PlacesModel(
                places=[
                    models.PlaceModel(
                        name="Airport Name",
                        country="Country",
                        latitude=90.0,  # noqa: WPS432
                        longitude=180.0,  # noqa: WPS432
                        iata_code=place,
                    )
                    for place in places["places"]
                ],
            ).model_dump(
                exclude_unset=True,
                by_alias=True,
            ),
            status_code=status.HTTP_200_OK,
        )
