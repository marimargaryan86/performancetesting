from starlette import endpoints, requests, responses, status

from snowfall.project.fti.service.bigxtra_api.routes import models
from snowfall.project.fti.service.bigxtra_api.schemas import SchemaGenerator


class AccommodationOffers(endpoints.HTTPEndpoint):
    @SchemaGenerator.schema(
        response_body=models.AccommodationsModel,
        query_parameters=models.AccommodationOffersQueryParams,
        description="Use this endpoint to list offers for accommodation only",
        summary="List Accommodation offers",
    )
    async def get(
        self,
        request: requests.Request,
    ) -> responses.JSONResponse:
        return responses.JSONResponse(
            content=models.AccommodationsModel(
                accommodations=[],
            ).model_dump(
                exclude_unset=True,
                by_alias=True,
            ),
            status_code=status.HTTP_200_OK,
        )


class PackageOffers(endpoints.HTTPEndpoint):
    @SchemaGenerator.schema(
        response_body=models.PackagesModel,
        query_parameters=models.PackageOffersQueryParams,
        description="Use this endpoint to list offers for tour packages",
        summary="List Package offers",
    )
    async def get(
        self,
        request: requests.Request,
    ) -> responses.JSONResponse:
        return responses.JSONResponse(
            content=models.PackagesModel(
                packages=[],
            ).model_dump(
                exclude_unset=True,
                by_alias=True,
            ),
            status_code=status.HTTP_200_OK,
        )
