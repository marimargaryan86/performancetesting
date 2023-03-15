import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.extensions.service.mobile_api import (
    repository,
    resources,
)
from snowfall.stdlib.integration.starlette import models


class Voucher(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        vouchers_repository: repository.VouchersRepository = lagom.injectable,
    ) -> responses.Response:
        voucher_code = request.path_params["voucherCode"]
        voucher = await vouchers_repository.find_voucher(voucher_code)
        if not voucher:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)
        return models.JsonApiResponse(
            models.Body(
                data=resources.VoucherResource.from_proto(voucher),
            ),
        )
