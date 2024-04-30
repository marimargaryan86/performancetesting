from datetime import date

import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.fti.service.bigxtra_api import repository
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
        fti_repository: repository.Repository = lagom.injectable,
    ) -> responses.JSONResponse:
        query_parameters = models.AccommodationOffersQueryParams.model_validate(
            request.query_params,
        )
        availabilities = await fti_repository.check_availability(
            date.fromisoformat(query_parameters.arrive_at),
            (
                date.fromisoformat(query_parameters.return_at)
                - date.fromisoformat(query_parameters.arrive_at)
            ).days,
            "A" * query_parameters.num_of_guests,
        )
        accommodations = [
            repository.Accommodations(
                id=availability[0],
                price_items=[
                    await fti_repository.get_price_item(
                        date.fromisoformat(query_parameters.arrive_at),
                        (
                            date.fromisoformat(query_parameters.return_at)
                            - date.fromisoformat(query_parameters.arrive_at)
                        ).days,
                        availability[0],
                        unit,
                    )
                    for unit in availability[1]
                ],
            )
            for availability in availabilities
        ]
        return responses.JSONResponse(
            content=models.AccommodationsModel(
                accommodations=[
                    models.AccommodationModel.from_model(price)
                    for price in accommodations
                ],
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
