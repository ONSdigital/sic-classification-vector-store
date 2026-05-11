"""Module that provides the SIC search-as-you-type endpoint."""

import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from survey_assist_utils.logging import get_logger
from survey_assist_utils.logging.logging_utils import SurveyAssistLogger

from sic_classification_vector_store.api.models.sayt import (
    SIC_SAYT_RESPONSE_EXAMPLE,
    SICSaytResponse,
)
from sic_classification_vector_store.utils.sayt import SaytManager

router = APIRouter(tags=["SIC SAYT"])
logger: SurveyAssistLogger = get_logger(__name__)


def get_sayt_manager(request: Request) -> SaytManager:
    """Get the warmed SAYT manager from FastAPI request state."""
    return request.state.sayt_manager


@router.get(
    "/sayt",
    response_model=SICSaytResponse,
    responses={
        200: {
            "description": "SIC search-as-you-type suggestions",
            "content": {"application/json": {"example": SIC_SAYT_RESPONSE_EXAMPLE}},
        }
    },
)
async def get_sic_sayt(
    description: str,
    sayt_manager: Annotated[SaytManager, Depends(get_sayt_manager)],
    num_suggestions: Annotated[int | None, Query(ge=1, le=100)] = None,
) -> SICSaytResponse:
    """Return SIC description suggestions as the user types."""
    start_time = time.perf_counter()

    if not description:
        raise HTTPException(status_code=400, detail="Description cannot be empty")

    try:
        suggestions = sayt_manager.suggest(description, num_suggestions)
    except RuntimeError as e:
        logger.error("SIC SAYT service unavailable", error=str(e))
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        logger.error("Error retrieving SIC SAYT suggestions", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving SIC SAYT suggestions: {e!s}",
        ) from e

    duration_ms = int((time.perf_counter() - start_time) * 1000)
    logger.info(
        "SIC SAYT response sent",
        suggestion_count=str(len(suggestions)),
        duration_ms=str(duration_ms),
    )
    return SICSaytResponse(suggestions=suggestions)
