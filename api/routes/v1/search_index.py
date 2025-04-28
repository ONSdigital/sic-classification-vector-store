"""Module that provides the search endpoint for the SIC Vector Store API.

This module contains the search endpoint for the SIC Vector Store API.
It defines the search endpoint and returns search results from the vector store.
"""

import logging

from fastapi import APIRouter, HTTPException, Request

from api.models.search_index import SearchIndexRequest, SearchIndexResponse
from utils.vector_store import vector_store_ready_event

logger = logging.getLogger(__name__)

router: APIRouter = APIRouter()


@router.post("/search-index", response_model=SearchIndexResponse)
async def post_search_index(
    request: Request, payload: SearchIndexRequest
) -> SearchIndexResponse:
    """Get the indexes from the vector store.

    Args:
        request: FastAPI request object
        payload: Search request payload

    Returns:
        SearchIndexResponse: Search results from the vector store

    Raises:
        HTTPException: If the vector store is not ready or there is an error searching
    """
    if not vector_store_ready_event.is_set():
        raise HTTPException(
            status_code=503,
            detail="Vector store is not ready",
        )

    try:
        search_results = request.app.state.embed.search_index_multi(
            query=[
                payload.industry_descr or "",
                payload.job_title or "",
                payload.job_description or "",
            ]
        )
        logger.info("Search completed successfully")
        return SearchIndexResponse(results=search_results)
    except Exception as e:
        logger.error("Error searching vector store: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error searching vector store: {e!s}",
        ) from e
