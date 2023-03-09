import lagom
from starlette import endpoints, exceptions, requests, status

from snowfall.project.pay.service.pay_api import resources
from snowfall.project.pay.service.pay_api.repositories import ConversionRepository
from snowfall.stdlib.integration.starlette import messages, models


class Conversions(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        conversion_repository: ConversionRepository = lagom.injectable,
    ) -> models.JsonApiResponse:
        conversion_id = request.path_params["conversionId"]

        conversion = await conversion_repository.find_by_id(conversion_id)
        if not conversion:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return await messages.create_response(
            body=messages.models.Body(
                data=resources.ConversionResource.from_proto(
                    conversion=conversion,
                ),
            ),
            request=request,
        )
