
from typing import Any

from fastapi import APIRouter, Body, HTTPException

from app.services.normalization import (
    normalization_service,
    NormalizationError,
    ApplicationMappingNotFound,
)


router = APIRouter(
    prefix="/applications",
    tags=["Application Integration"]
)


@router.post("/{application_id}/normalize")
async def normalize_application_payload(
    application_id: str,
    payload: dict[str, Any] = Body(...)
):
    """
    Receive an application-specific JSON payload
    and convert it into the canonical recommendation request.
    """

    try:
        normalized_request = normalization_service.normalize(
            application_id=application_id,
            payload=payload
        )

        return {
            "success": True,
            "application_id": application_id,
            "mapping_version": (
                normalization_service
                .load_mapping(application_id)
                .version
            ),
            "contract_version": "1.0.0",
            "message": "Application payload successfully normalised.",
            "request_id": str(normalized_request.request_id),
            "normalized_request": normalized_request.model_dump(
                mode="json"
            )
        }

    except ApplicationMappingNotFound as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )

    except NormalizationError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )
