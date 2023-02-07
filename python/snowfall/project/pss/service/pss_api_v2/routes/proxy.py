from fastapi import Depends
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.routing import APIRouter

from snowfall.project.pss.service.pss_api_v2.services.proxy import ProxyService

router = APIRouter()


@router.api_route("/{request_path:path}", methods=["GET", "POST", "PATCH", "DELETE"])
async def _proxy_call(
    request: Request,
    proxy_service: ProxyService = Depends(ProxyService),
) -> Response:
    return await proxy_service.proxy_request(request)
