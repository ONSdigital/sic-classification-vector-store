"""Module that provides the configuration endpoint for the Survey Assist API.

This module contains the configuration endpoint for the Survey Assist API.
It defines the configuration endpoint and returns the current configuration settings.
"""

from fastapi import APIRouter, Request

from api.models.search_index import SearchIndexRequest, SearchIndexResponse

router: APIRouter = APIRouter()


@router.post("/search-index", response_model=SearchIndexResponse)
async def post_search_index(
    request: Request, payload: SearchIndexRequest
) -> SearchIndexResponse:
    """Get the indexes from the vector store.

    Returns:
        SearchIndexResponse: A dictionary containing the current status.
    """
    results = request.app.state.embed.search_index_multi(
        query=[
            payload.industry_descr or "",
            payload.job_title or "",
            payload.job_description or "",
        ]
    )
    print(f"Results: {results}")
    return results
