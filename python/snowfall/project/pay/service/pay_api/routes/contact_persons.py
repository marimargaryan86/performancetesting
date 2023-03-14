import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.pay.service.accounts import accounts
from snowfall.project.pay.service.accounts.v1alpha import models_pb2
from snowfall.project.pay.service.pay_api import resources
from snowfall.project.pay.service.pay_api.repositories import CompanyRepository
from snowfall.stdlib import string
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    request_helpers,
)
from snowfall.stdlib.v1alpha import phone_number_pb2


class ContactPersons(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        contact_person_repository: accounts.ContactPersonsRepository = lagom.injectable,
        companies_repository: CompanyRepository = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        company = await companies_repository.find_by_id(body["company"])

        if not company:
            return models.JsonApiResponse(
                body=messages.models.Body(
                    errors=[
                        messages.models.Error(
                            status=str(status.HTTP_404_NOT_FOUND),
                            code="not_found",
                            detail="Company does not exists",
                            source=messages.models.ErrorSource(
                                pointer="/data/relationships/company/data/id",
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_404_NOT_FOUND,
            )

        contact_person = await contact_person_repository.insert(
            models_pb2.ContactPerson(
                id=string.uuid(),
                first_name=body["firstName"],
                last_name=body["lastName"],
                email=body["emailAddress"],
                phone_number=phone_number_pb2.PhoneNumber(
                    e164_number=body["phoneNumber"],
                ),
                company_id=company.id,
            ),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.ContactPersonResource.from_proto(
                    contact_person=contact_person,
                ),
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )

    async def get(
        self,
        request: requests.Request,
        contact_person_repository: accounts.ContactPersonsRepository = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)

        contact_persons = await contact_person_repository.find_by_company_id(
            request.query_params["company"],
            pagination.cursor,
            pagination.limit,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.ContactPersonResource.from_proto(contact_person)
                    async for contact_person in contact_persons
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("ContactPerson").include_query_params(
                        company=request.query_params["company"],
                    ),
                    await contact_persons.cursor(),
                    pagination,
                ),
            ),
            request=request,
        )
