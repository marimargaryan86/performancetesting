import lagom
from starlette import endpoints, requests, status

from snowfall.project.junction.service.pay_api import resources
from snowfall.project.junction.service.pay_api.repositories import CompanyRepository
from snowfall.project.pay.service.companies.v1alpha import models_pb2
from snowfall.stdlib.integration.starlette import messages, models, request_helpers
from snowfall.stdlib.v1alpha import postal_address_pb2


class StoreCompany(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        companies_repository: CompanyRepository = lagom.injectable,
    ) -> models.JsonApiResponse:
        body = await request_helpers.flatten_request(request)
        address = body["address"]
        company = await companies_repository.insert(
            models_pb2.Company(
                name=body["name"],
                address=postal_address_pb2.PostalAddress(
                    address_lines=address["addressLines"],
                    region_code=address["countryCode"],
                    postal_code=address["postalCode"],
                    locality=address["city"],
                    revision=0,
                ),
                buffer_rate=float(body["bufferRate"]),
                sales_rate=float(body["salesRate"]),
            ),
        )

        return await messages.create_response(
            body=messages.models.Body(
                data=resources.Company.from_proto(
                    company=company,
                ),
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )
