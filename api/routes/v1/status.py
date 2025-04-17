"""Module that provides the configuration endpoint for the Survey Assist API.

This module contains the configuration endpoint for the Survey Assist API.
It defines the configuration endpoint and returns the current configuration settings.
"""

from fastapi import APIRouter

from api.models.status import StatusResponse
from utils.common import safe_int
from utils.vector_store import (
    vector_store_ready_event,
    vector_store_status,
)

router: APIRouter = APIRouter()

# Mock configuration
status_resp: StatusResponse = StatusResponse(
    status="starting",
    embedding_model_name=str(vector_store_status.get("embedding_model_name", "")),
    llm_model_name=str(vector_store_status.get("llm_model_name", "")),
    db_dir=str(vector_store_status.get("db_dir", "")),
    sic_index_file=str(vector_store_status.get("sic_index", "")),
    sic_structure_file=str(vector_store_status.get("sic_structure", "")),
    sic_condensed_file=str(vector_store_status.get("sic_condensed", "")),
    matches=safe_int(vector_store_status.get("matches", 0)),
    index_size=safe_int(vector_store_status.get("index_size", 0)),
)


@router.get("/status", response_model=StatusResponse)
async def get_status() -> StatusResponse:
    """Get the current status of the vector store.

    Returns:
        StatusResponse: A dictionary containing the current status.
    """
    status_resp.status = "ready" if vector_store_ready_event.is_set() else "loading"
    status_resp.embedding_model_name = str(
        vector_store_status.get("embedding_model_name", "")
    )
    status_resp.llm_model_name = str(vector_store_status.get("llm_model_name", ""))
    status_resp.db_dir = str(vector_store_status.get("db_dir", ""))
    status_resp.sic_index_file = str(vector_store_status.get("sic_index", ""))
    status_resp.sic_structure_file = str(vector_store_status.get("sic_structure", ""))
    status_resp.sic_condensed_file = str(vector_store_status.get("sic_condensed", ""))
    status_resp.matches = safe_int(
        vector_store_status.get("matches", 0)
    )  # Assuming matches is an int
    status_resp.index_size = safe_int(
        vector_store_status.get("index_size", 0)
    )  # Assuming index_size is an int
    return status_resp
