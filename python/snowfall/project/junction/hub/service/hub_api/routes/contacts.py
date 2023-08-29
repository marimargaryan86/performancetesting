import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.hub.service.hub_api import resources
from snowfall.project.pay.adapter import contacts as contacts_adapter
from snowfall.project.pay.service.companies.v1alpha import models_pb2
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    request_helpers,
)
from snowfall.stdlib.v1 import phone_number_pb2


class Contacts(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        contacts_client: contacts_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        contact = await contacts_client.create(
            models_pb2.Contact(
                first_name=body["firstName"],
                last_name=body["lastName"],
                email=body["emailAddress"],
                phone_number=phone_number_pb2.PhoneNumber(
                    e164_number=body["phoneNumber"],
                ),
                company_id=request.path_params["companyId"],
            ),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.ContactResource.from_proto(
                    contact=contact,
                ),
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )

    async def get(
        self,
        request: requests.Request,
        contacts_client: contacts_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)

        response = await contacts_client.find_by_company_id(
            request.path_params["companyId"],
            pagination.cursor,
            pagination.limit,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.ContactResource.from_proto(contact)
                    for contact in response.contacts
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for(
                        "Contact",
                        companyId=request.path_params["companyId"],
                    ),
                    response.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )
