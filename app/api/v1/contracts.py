from fastapi import APIRouter

from app.schemas.recommendation import RecommendationRequest


router = APIRouter(
    prefix="/contracts",
    tags=["API Contracts"]
)


@router.post("/recommendations/validate")
async def validate_recommendation_request(
    request: RecommendationRequest
):
    """
    Validate and normalise an incoming recommendation request.

    This endpoint does not execute a recommendation algorithm.
    It establishes whether an application can communicate
    successfully using the canonical gateway contract.
    """

    return {
        "success": True,
        "contract_version": "1.0.0",
        "message": "Recommendation request successfully validated.",
        "request_id": str(request.request_id),
        "normalized_request": request.model_dump(mode="json")
    }