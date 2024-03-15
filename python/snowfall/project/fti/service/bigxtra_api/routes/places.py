from pydantic import Field
from starlette import endpoints, requests, responses, status

from snowfall.project.fti.service.bigxtra_api.models import (
    BaseModel,
    PaginationQueryParams,
)
from snowfall.project.fti.service.bigxtra_api.schemas import SchemaGenerator


class PlaceModel(BaseModel):
    name: str = Field(json_schema_extra={"example": "Athens"})
    country: str = Field(json_schema_extra={"example": "Greece"})
    latitude: float = Field(json_schema_extra={"example": 90.0})
    longitude: float = Field(json_schema_extra={"example": 180.0})


class PlacesModel(BaseModel):
    places: list[PlaceModel]


class Places(endpoints.HTTPEndpoint):
    @SchemaGenerator.schema(
        response_body=PlacesModel,
        query_parameters=PaginationQueryParams,
        status_code=status.HTTP_200_OK,
        description="Use this endpoint to list Places",
        summary="List places",
    )
    async def get(
        self,
        request: requests.Request,
    ) -> responses.JSONResponse:
        return responses.JSONResponse(
            content=PlacesModel(
                places=[
                    PlaceModel(
                        name="Athens",
                        country="Greece",
                        latitude=90.0,  # noqa: WPS432
                        longitude=180.0,  # noqa: WPS432
                    ),
                ],
            ).model_dump(
                exclude_unset=True,
                by_alias=True,
            ),
            status_code=status.HTTP_200_OK,
        )
