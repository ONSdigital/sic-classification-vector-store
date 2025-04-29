"""Module that provides the configuration endpoint for the Survey Assist API.

This module contains the configuration endpoint for the Survey Assist API.
It defines the configuration endpoint and returns the current configuration settings.
"""

from fastapi import APIRouter, Depends

from api.models.status import StatusResponse
from utils.common import safe_int
from utils.vector_store import vector_store_manager

router = APIRouter(tags=["Status"])


def get_vector_store():
    """Get a vector store instance.

    Returns:
        VectorStoreManager: A vector store manager instance.
    """
    return vector_store_manager


# Define the dependency at module level
vector_store_dependency = Depends(get_vector_store)


@router.get("/status", response_model=StatusResponse)
async def get_status(vector_store=vector_store_dependency) -> StatusResponse:
    """Get the current status of the vector store.

    Args:
        vector_store: Vector store manager instance

    Returns:
        StatusResponse: A dictionary containing the current status.
    """
    status_resp = StatusResponse(
        status="ready" if vector_store.ready_event.is_set() else "loading",
        embedding_model_name=str(vector_store.status.get("embedding_model_name", "")),
        llm_model_name=str(vector_store.status.get("llm_model_name", "")),
        db_dir=str(vector_store.status.get("db_dir", "")),
        sic_index_file=str(vector_store.status.get("sic_index", "")),
        sic_structure_file=str(vector_store.status.get("sic_structure", "")),
        sic_condensed_file=str(vector_store.status.get("sic_condensed", "")),
        matches=safe_int(vector_store.status.get("matches", 0)),
        index_size=safe_int(vector_store.status.get("index_size", 0)),
    )
    return status_resp
