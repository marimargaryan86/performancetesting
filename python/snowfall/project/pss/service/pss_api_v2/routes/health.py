from fastapi.routing import APIRouter

from snowfall.project.pss.service.pss_api_v2.schemas.health import HealthSchema

router = APIRouter()


@router.get("", response_model=HealthSchema)
def _get_health() -> HealthSchema:
    return HealthSchema(message="pass")
