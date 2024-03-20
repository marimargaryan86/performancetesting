import lagom
from pydantic import Field
from starlette import endpoints, requests, responses, status

from snowfall.project.fti.service.bigxtra_api import repository
from snowfall.project.fti.service.bigxtra_api.models import (
    BaseModel,
)
from snowfall.project.fti.service.bigxtra_api.schemas import SchemaGenerator


class PlaceModel(BaseModel):
    name: str = Field(json_schema_extra={"example": "Athens"})
    country: str = Field(json_schema_extra={"example": "Greece"})
    latitude: float = Field(json_schema_extra={"example": 90.0})
    longitude: float = Field(json_schema_extra={"example": 180.0})
    iata_code: str = Field(
        default="",
        json_schema_extra={"nullable": True, "example": "ATH"},
    )


class PlacesModel(BaseModel):
    places: list[PlaceModel]


class PlacesQueryParams(BaseModel):
    destination: str = Field(
        default="",
        json_schema_extra={
            "nullable": True,
            "example": "ATH",
            "description": "If set, the endpoint returns places connected to this destination place.",
        },
    )


class Places(endpoints.HTTPEndpoint):
    @SchemaGenerator.schema(
        response_body=PlacesModel,
        query_parameters=PlacesQueryParams,
        description="Use this endpoint to list Places",
        summary="List places",
    )
    async def get(
        self,
        request: requests.Request,
        places_repository: repository.PlacesRepository = lagom.injectable,
    ) -> responses.JSONResponse:
        query_params = PlacesQueryParams.model_validate(request.query_params)
        result = await places_repository.find_places(query_params.destination)
        places = await result.take()
        return responses.JSONResponse(
            content=PlacesModel(
                places=[
                    PlaceModel(
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
