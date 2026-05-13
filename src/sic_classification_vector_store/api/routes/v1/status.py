"""Module that provides the configuration endpoint for the Survey Assist API.

This module contains the configuration endpoint for the Survey Assist API.
It defines the configuration endpoint and returns the current configuration settings.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from sic_classification_vector_store.api.models.status import StatusResponse
from sic_classification_vector_store.utils.common import safe_int
from sic_classification_vector_store.utils.vector_store import (
    VectorStoreManager,
    vector_store_manager,
)

router = APIRouter(tags=["Status"])


def get_vector_store():
    """Get a vector store instance.

    Returns:
        VectorStoreManager: A vector store manager instance.
    """
    return vector_store_manager


@router.get("/status", response_model=StatusResponse)
async def get_status(
    vector_store: Annotated[VectorStoreManager, Depends(get_vector_store)],
) -> StatusResponse:
    """Get the current status of the vector store.

    Args:
        vector_store: Vector store manager instance

    Returns:
        StatusResponse: A dictionary containing the current status.
    """
    config_data = vector_store.config_data if vector_store.embed else {}
    status_resp = StatusResponse(
        status=_resolve_status(vector_store),
        embedding_model_name=str(config_data.get("embedding_model_name", "")),
        db_dir=str(config_data.get("db_dir", "")),
        index_source_file=str(config_data.get("index_source_file", "")),
        k_matches=safe_int(config_data.get("k_matches", 0)),
        index_size=safe_int(config_data.get("index_size", 0)),
    )
    return status_resp


def _resolve_status(vector_store: VectorStoreManager) -> str:
    """Resolve the current vector store lifecycle status."""
    if vector_store.load_error is not None:
        return "error"

    if vector_store.ready_event.is_set() and vector_store.embed is not None:
        return "ready"

    return "loading"


# %%
