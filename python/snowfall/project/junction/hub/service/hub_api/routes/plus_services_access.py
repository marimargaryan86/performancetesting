import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.hub.service.hub_api import resources
from snowfall.project.junction.hub.service.hub_api.permissions import check_permission
from snowfall.project.junction.plus.adapter import (
    configuration_vectors as config_vector_adapter,
)
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
)


class PlusServicesAccess(endpoints.HTTPEndpoint):
    async def patch(
        self,
        request: requests.Request,
        config_vector_client: config_vector_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        check_permission("plus.permissions.edit", request.user.permissions)
        reseller_id = request.path_params["resellerId"]
        payload = await request.json()
        updates = [
            config_vector_adapter.PermissionUpdate(**item["attributes"])
            for item in payload["data"]
        ]

        await config_vector_client.update_permissions(
            reseller_id=reseller_id,
            updates=updates,
        )

        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)

    async def get(
        self,
        request: requests.Request,
        config_vector_client: config_vector_adapter.Client = lagom.injectable,
    ) -> models.JsonApiResponse:
        check_permission("plus.permissions.view", request.user.permissions)
        reseller_id = request.path_params["resellerId"]
        permissions = await config_vector_client.get_permissions(
            reseller_id=reseller_id,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.PlusServiceAccess.from_dict(
                        permission=permission,
                    )
                    for permission in permissions
                ],
            ),
            request=request,
        )
