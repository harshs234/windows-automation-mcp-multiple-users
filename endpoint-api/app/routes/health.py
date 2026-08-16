from fastapi import APIRouter
from app.models.health_response import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    tags=["Health"],
    summary="Check API health status",
    response_model=HealthResponse,
)
def get_health():
    return HealthResponse(status="online", version="2.0.0")
