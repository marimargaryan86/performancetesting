import lagom
from starlette import endpoints, exceptions, requests, status

from snowfall.project.pay.service.pay_api import repositories, resources
from snowfall.stdlib.integration.starlette import messages, models, pagination_helpers


class Conversions(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        conversion_repository: repositories.ConversionRepository = lagom.injectable,
        transaction_repository: repositories.TransactionRepository = lagom.injectable,
    ) -> models.JsonApiResponse:
        conversion_id = request.path_params["conversionId"]

        conversion = await conversion_repository.find_by_id(conversion_id)
        if not conversion:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        transaction = await transaction_repository.find_by_id(
            conversion.id,
            "conversion_id",
        )
        if transaction is None:
            return await messages.create_response(
                body=messages.models.Body(
                    data=resources.ConversionResource.from_proto(
                        conversion=conversion,
                        fx_delta=None,
                        transaction_id=None,
                        request=request,
                    ),
                ),
                request=request,
            )

        return await messages.create_response(
            body=messages.models.Body(
                data=resources.ConversionResource.from_proto(
                    conversion=conversion,
                    fx_delta=round(
                        conversion.executed_rate - transaction.rates.fx_quote,
                        3,
                    ),
                    transaction_id=transaction.id,
                    request=request,
                ),
            ),
            request=request,
        )


class ListConversions(endpoints.HTTPEndpoint):
    _default_page_size = 20

    async def get(  # noqa: WPS210
        self,
        request: requests.Request,
        conversion_repository: repositories.ConversionRepository = lagom.injectable,
        transaction_repository: repositories.TransactionRepository = lagom.injectable,
    ) -> models.JsonApiResponse:
        pagination = pagination_helpers.get_pagination(request)

        conversions = await conversion_repository.find(
            cursor=pagination.cursor,
        )

        conversions.limit(pagination.limit or self._default_page_size)

        conversion_resources = []
        async for conversion in conversions:
            transaction = await transaction_repository.find_by_id(
                conversion.id,
                "conversion_id",
            )

            if transaction is None:
                conversion_resources.append(
                    resources.ConversionResource.from_proto(
                        conversion=conversion,
                        fx_delta=None,
                        transaction_id=None,
                        request=request,
                    ),
                )
                continue

            conversion_resources.append(
                resources.ConversionResource.from_proto(
                    conversion=conversion,
                    fx_delta=round(
                        conversion.executed_rate - transaction.rates.fx_quote,
                        3,
                    ),
                    transaction_id=transaction.id,
                    request=request,
                ),
            )
        list_conversion_url = request.url_for("ListConversion")
        includes = request.scope["query_string"].get("include")
        if includes is not None:
            list_conversion_url = list_conversion_url.include_query_params(
                include=",".join(includes),
            )

        return await messages.create_response(
            body=messages.models.Body(
                data=conversion_resources,
                links=pagination_helpers.get_next_url(
                    list_conversion_url,
                    await conversions.cursor(),
                    pagination,
                ),
            ),
            request=request,
        )
