"""Health check router."""

from fastapi import APIRouter, status
from app.schemas.task import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check the operational health and availability of the TaskFlow API.",
)
def get_health() -> HealthResponse:
    """Return API health status."""
    return HealthResponse(status="ok")
