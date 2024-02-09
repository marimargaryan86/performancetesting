import asyncio
import dataclasses

import lagom
from starlette import endpoints, requests, responses, status

from snowfall.adapter import identities as identities_adapter
from snowfall.project.junction.go.adapter import resellers
from snowfall.project.junction.hub.service.hub_api import repository, resources
from snowfall.project.junction.hub.service.hub_api.permissions import check_permission
from snowfall.project.junction.hub.service.hub_api.v1 import models_pb2
from snowfall.project.pay.adapter import companies as companies_adapter
from snowfall.project.pay.adapter import contacts as contacts_adapter
from snowfall.service.authentication.v1 import identities_pb2
from snowfall.stdlib import string
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
    _users_repository: repository.UsersRepository

    async def view(self, request: messages.Request) -> responses.Response:
        check_permission("user.view", request.starlette_request.user.permissions)
        user_id = request.path_params["userId"]
        user = await self._identities_client.get_ory_identity(identifier=user_id)
        return await messages.create_response(
            body=models.Body(data=resources.UserResource.from_proto(user)),
            request=request.starlette_request,
        )

    async def delete(self, request: messages.Request) -> responses.Response:
        check_permission("user.delete", request.starlette_request.user.permissions)

        user_id = request.path_params["userId"]
        await self._identities_client.delete_ory_identity(
            identifier=user_id,
        )

        await self._delete_user_in_users_repository(user_id)

        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)

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
            await self._resellers_client.get_reseller(reseller_id)

            metadata = {**metadata, "reseller_id": reseller_id}

        ory_identity = await self._identities_client.create_ory_identity(
            email=body["email"],
            metadata=metadata,
        )

        await self._add_new_user_to_users_repository(ory_identity)

        return await messages.create_response(
            body=models.Body(data=resources.UserResource.from_proto(ory_identity)),
            status_code=status.HTTP_201_CREATED,
            request=request.starlette_request,
        )

    async def patch(
        self,
        request: messages.Request,
    ) -> responses.Response:
        check_permission(
            "user.edit",
            request.starlette_request.user.permissions,
        )

        body = await request_helpers.flatten_request(request.starlette_request)

        user_id = request.path_params["userId"]

        ory_identity = await self._identities_client.update_ory_identity(
            identifier=user_id,
            email=body["email"],
            metadata={"role": body["role"], "reseller_id": body["reseller"]},
        )

        await self._update_user_in_users_repository(ory_identity)

        return await messages.create_response(
            body=models.Body(data=resources.UserResource.from_proto(ory_identity)),
            request=request.starlette_request,
        )

    async def _update_user_in_users_repository(
        self,
        ory_identity: identities_pb2.Identity,
    ) -> None:
        user = await self._users_repository.find_by_ory_identity_id(ory_identity.id)
        metadata = dict(ory_identity.metadata_public.items())
        identity_reseller_id = str(metadata.get("reseller_id", ""))
        if not user:
            user = models_pb2.User(
                id=string.uuid(),
                ory_identity_id=ory_identity.id,
                reseller_id=identity_reseller_id,
            )

        user.reseller_id = identity_reseller_id
        await self._users_repository.upsert(user)

    async def _delete_user_in_users_repository(
        self,
        user_id: str,
    ) -> None:
        await self._users_repository.delete_by_ory_identity_id(user_id)

    async def _add_new_user_to_users_repository(
        self,
        ory_identity: identities_pb2.Identity,
    ) -> None:
        metadata = dict(ory_identity.metadata_public.items())
        identity_reseller_id = str(metadata.get("reseller_id", ""))

        new_user = models_pb2.User(
            id=string.uuid(),
            ory_identity_id=ory_identity.id,
            reseller_id=identity_reseller_id,
        )

        await self._users_repository.insert(new_user)


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
