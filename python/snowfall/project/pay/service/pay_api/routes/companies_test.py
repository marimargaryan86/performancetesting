import httpx
from starlette import status

from snowfall.project.pay.service.companies.v1alpha.models_pb2 import Company


class TestCompanies(object):
    async def test_get_company_details_success(
        self,
        admin_client: httpx.AsyncClient,
        valid_company: Company,
    ) -> None:
        response = await admin_client.get(
            "/companies/{company_id}".format(company_id=valid_company.id),
        )

        assert response.status_code == status.HTTP_200_OK
