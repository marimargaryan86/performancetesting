import lagom
from starlette import endpoints, requests

from snowfall.project.junction.go.adapter import errors
from snowfall.project.junction.hub.service.hub_api import resources
from snowfall.project.pay.adapter import conversions as conversions_adapter
from snowfall.project.pay.adapter import transactions as transactions_adapter
from snowfall.stdlib.integration.starlette import messages, models, pagination_helpers


class Conversions(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        conversion_client: conversions_adapter.Client = lagom.injectable,
        transactions_client: transactions_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        conversion_id = request.path_params["conversionId"]

        conversion = await conversion_client.get(conversion_id)

        try:
            transaction = await transactions_client.get(conversion.id, "conversion_id")
        except errors.NotFoundError:
            return await messages.create_response(
                body=models.Body(
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
            body=models.Body(
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

    async def get(
        self,
        request: requests.Request,
        conversion_client: conversions_adapter.Client = lagom.injectable,
        transactions_client: transactions_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        pagination = pagination_helpers.get_pagination(request)

        response = await conversion_client.find(
            limit=pagination.limit or self._default_page_size,
            cursor=pagination.cursor,
        )

        conversion_resources = []
        for conversion in response.conversions:
            try:
                transaction = await transactions_client.get(
                    conversion.id,
                    "conversion_id",
                )
            except errors.NotFoundError:
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
        includes = request.scope["parsed_query_string"].get("include")
        if includes is not None:
            list_conversion_url = list_conversion_url.include_query_params(
                include=",".join(includes),
            )

        return await messages.create_response(
            body=models.Body(
                data=conversion_resources,
                links=pagination_helpers.get_next_url(
                    list_conversion_url,
                    response.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )
