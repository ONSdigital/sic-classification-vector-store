"""Module that provides the search endpoint for the SIC Vector Store API.

This module contains the search endpoint for the SIC Vector Store API.
It defines the search endpoint and returns search results from the vector store.
"""

from fastapi import APIRouter, HTTPException, Request
from industrial_classification_utils.embed import SearchIndexResponse
from survey_assist_utils.logging import get_logger

from sic_classification_vector_store.api.models.search_index import (
    SearchIndexRequest,
)
from sic_classification_vector_store.utils.vector_store import vector_store_manager

logger = get_logger(__name__)

router: APIRouter = APIRouter()


@router.post("/search-index", response_model=SearchIndexResponse)
async def post_search_index(
    _request: Request, payload: SearchIndexRequest
) -> SearchIndexResponse:
    """Get the indexes from the vector store.

    Args:
        _request: FastAPI request object (unused)
        payload: Search request payload

    Returns:
        SearchIndexResponse: Search results from the vector store

    Raises:
        HTTPException: If the vector store is not ready or there is an error searching
    """
    try:
        search_results = vector_store_manager.search(
            industry_descr=payload.industry_descr,
            job_title=payload.job_title,
            job_description=payload.job_description,
        )
        logger.info("Search completed successfully")
        return search_results
    except RuntimeError as e:
        logger.error(f"Vector store error: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Error searching vector store: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error searching vector store: {e!s}",
        ) from e
