from pydantic import Field
from starlette import endpoints, requests, responses, status

from snowfall.project.fti.service.bigxtra_api.models import (
    BaseModel,
    PaginationQueryParams,
)
from snowfall.project.fti.service.bigxtra_api.schemas import SchemaGenerator
from snowfall.stdlib import string


class ExampleModel(BaseModel):
    example_id: str = Field(
        json_schema_extra={"format": "uuid", "readOnly": True},
    )
    example_number: int = Field(json_schema_extra={"example": 20})  # noqa: WPS432
    example_details: str


class ExamplesModel(BaseModel):
    examples: list[ExampleModel]


class PathParams(BaseModel):
    example_id: str = Field(
        json_schema_extra={"format": "uuid", "description": "The ID of the example"},
    )


class Examples(endpoints.HTTPEndpoint):
    @SchemaGenerator.schema(
        response_body=ExamplesModel,
        query_parameters=PaginationQueryParams,
        status_code=status.HTTP_201_CREATED,
        description="Use this endpoint to get Examples",
        summary="List examples",
    )
    async def get(
        self,
        request: requests.Request,
    ) -> responses.JSONResponse:
        return responses.JSONResponse(
            content=ExamplesModel(
                examples=[
                    ExampleModel(
                        example_id=string.uuid(),
                        example_number=2,
                        example_details="Some details",
                    ),
                ],
            ).model_dump(
                exclude_unset=True,
                by_alias=True,
            ),
            status_code=status.HTTP_201_CREATED,
        )

    @SchemaGenerator.schema(
        request_body=ExampleModel,
        status_code=status.HTTP_204_NO_CONTENT,
        description="Use this endpoint to create an Example",
        summary="Create example",
    )
    async def post(
        self,
        request: requests.Request,
    ) -> responses.JSONResponse:
        return responses.JSONResponse(
            content=ExamplesModel(
                examples=[
                    ExampleModel(
                        example_id=string.uuid(),
                        example_number=2,
                        example_details="Some details",
                    ),
                ],
            ).model_dump(
                exclude_unset=True,
                by_alias=True,
            ),
            status_code=status.HTTP_204_NO_CONTENT,
        )


class Example(endpoints.HTTPEndpoint):
    @SchemaGenerator.schema(
        response_body=ExampleModel,
        path_parameters=PathParams,
        description="Get an example based on the provided example id",
        summary="Get example",
    )
    async def get(
        self,
        request: requests.Request,
    ) -> responses.JSONResponse:
        return responses.JSONResponse(
            content=ExamplesModel(
                examples=[
                    ExampleModel(
                        example_id=string.uuid(),
                        example_number=2,
                        example_details="Some details",
                    ),
                ],
            ).model_dump(
                exclude_unset=True,
                by_alias=True,
            ),
            status_code=status.HTTP_200_OK,
        )
