import asyncio
import dataclasses

import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.go.adapter import resellers
from snowfall.project.junction.hub.service.hub_api import resources
from snowfall.project.junction.hub.service.hub_api.permissions import check_permission
from snowfall.project.pay.adapter import companies as companies_adapter
from snowfall.project.pay.adapter import contacts as contacts_adapter
from snowfall.stdlib.integration.starlette import messages, models, pagination_helpers


@dataclasses.dataclass(frozen=True)
class Users(object):
    async def view(self, request: messages.Request) -> responses.Response:
        check_permission("user.view", request.starlette_request.user.permissions)

        raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

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

        return await messages.create_response(
            body=models.Body(
                data=resources.UsersProfileResource.from_proto(
                    reseller_id=reseller_id,
                    company=company,
                    contacts=contacts.contacts,
                ),
            ),
            request=request,
        )
