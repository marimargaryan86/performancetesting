from __future__ import annotations

from typing import ClassVar

from snowfall.project.pay.service.companies.v1alpha import models_pb2
from snowfall.stdlib.integration.starlette import models


class Company(models.Resource):
    api_type: ClassVar[str] = "companies"

    @classmethod
    def from_proto(
        cls,
        company: models_pb2.Company,
    ) -> Company:
        return cls(
            id=company.id,
            type=Company.api_type,
            attributes={
                "name": company.name,
                "address": {
                    "addressLines": list(company.address.address_lines),
                    "countryCode": company.address.region_code,
                    "postalCode": company.address.postal_code,
                    "city": company.address.locality,
                },
                "bufferRate": round(company.buffer_rate, 3),
                "salesRate": round(company.sales_rate, 3),
            },
        )
