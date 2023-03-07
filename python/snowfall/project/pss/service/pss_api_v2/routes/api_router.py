from fastapi.routing import APIRouter

from snowfall.project.pss.service.pss_api_v2.routes import (
    accounts,
    accounts_admin,
    countries,
    health,
    proxy,
    transactions,
)

router = APIRouter()

router.include_router(accounts_admin.router, prefix="/admin", tags=["admin"])
router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
router.include_router(countries.router, prefix="/countries", tags=["countries"])
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(
    transactions.router,
    prefix="/transactions",
    tags=["transactions"],
)
router.include_router(proxy.router)
