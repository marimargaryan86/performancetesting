from fastapi.routing import APIRouter

from snowfall.project.pss.service.api.routes import accounts, countries

router = APIRouter()

router.include_router(countries.router, prefix="/countries", tags=["countries"])
router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
