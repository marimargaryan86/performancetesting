import asyncio
import dataclasses

import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.adapter import identities as identities_adapter
from snowfall.project.junction.go.adapter import errors, resellers
from snowfall.project.junction.hub.service.hub_api import resources
from snowfall.project.junction.hub.service.hub_api.permissions import check_permission
from snowfall.project.pay.adapter import companies as companies_adapter
from snowfall.project.pay.adapter import contacts as contacts_adapter
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    request_helpers,
)


@dataclasses.dataclass(frozen=True)
class Users(object):
    _identities_client: identities_adapter.Client
    _resellers_client: resellers.Client

    async def view(self, request: messages.Request) -> responses.Response:
        check_permission("user.view", request.starlette_request.user.permissions)

        raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

    async def delete(self, request: messages.Request) -> responses.Response:
        check_permission("user.delete", request.starlette_request.user.permissions)
        user_id = request.path_params["userId"]
        await self._identities_client.delete_ory_identity(
            identifier=user_id,
        )
        return await messages.create_response(
            body=models.Body(data=None),
            request=request.starlette_request,
            status_code=status.HTTP_204_NO_CONTENT,
        )

    async def list_(self, request: messages.Request) -> responses.Response:
        check_permission("user.view", request.starlette_request.user.permissions)

        return models.JsonApiResponse(
            models.Body(
                data=[],
                links=pagination_helpers.get_next_url(
                    request.starlette_request.url_for("ListUsers"),
                    "",
                    request.pagination,
                ),
            ),
        )

    async def post(
        self,
        request: messages.Request,
    ) -> responses.Response:
        check_permission(
            "user.add",
            request.starlette_request.user.permissions,
        )

        body = await request_helpers.flatten_request(request.starlette_request)

        metadata = {"role": body["role"]}
        reseller_id = body["reseller"]

        if reseller_id:
            try:
                await self._resellers_client.get_reseller(reseller_id)
            except errors.NotFoundError:
                return await messages.create_response(
                    request=request.starlette_request,
                    body=models.Body(
                        errors=[
                            models.Error(
                                status=str(status.HTTP_400_BAD_REQUEST),
                                code="bad_request",
                                detail="Reseller does not exists",
                                source=models.ErrorSourcePointer(
                                    pointer="/data/relationships/reseller/data/id",
                                ),
                            ),
                        ],
                    ),
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            metadata = {**metadata, "reseller_id": reseller_id}

        user = await self._identities_client.create_ory_identity(
            email=body["email"],
            metadata=metadata,
        )

        return await messages.create_response(
            body=models.Body(data=resources.UserResource.from_proto(user)),
            status_code=status.HTTP_201_CREATED,
            request=request.starlette_request,
        )


class UserInformation(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        companies_client: companies_adapter.Client = lagom.injectable,
        contacts_client: contacts_adapter.Client = lagom.injectable,
        resellers_client: resellers.Client = lagom.injectable,
    ) -> responses.Response:
        reseller_id = request.user.metadata.get("reseller_id", "")
        reseller = await resellers_client.get_reseller(reseller_id)

        company, contacts = await asyncio.gather(
            companies_client.get(reseller.company_id),
            contacts_client.find_by_company_id(
                company_id=reseller.company_id,
            ),
        )

        data = resources.UsersProfileResource.from_proto(
            reseller_id=reseller_id,
            company=company,
            contacts=contacts.contacts,
        )
        data.attributes["permissions"].update(request.user.permissions)

        return await messages.create_response(
            body=models.Body(data=data),
            request=request,
        )
