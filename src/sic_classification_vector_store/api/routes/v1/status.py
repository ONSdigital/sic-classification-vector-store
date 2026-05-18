"""Module that provides the configuration endpoint for the Survey Assist API.

This module contains the configuration endpoint for the Survey Assist API.
It defines the configuration endpoint and returns the current configuration settings.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from industrial_classification_utils.models.config_model import EmbeddingStatus
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


@router.get("/status", response_model=EmbeddingStatus)
async def get_status(
    vector_store: Annotated[VectorStoreManager, Depends(get_vector_store)],
) -> EmbeddingStatus:
    """Get the current status of the vector store.

    Args:
        vector_store: Vector store manager instance

    Returns:
        EmbeddingStatus: A dictionary containing the current status.
    """    
    status_str = _resolve_status(vector_store)
    if status_str == "ready" and vector_store.embed is not None:
        return vector_store.embed.get_embed_config()
    return EmbeddingStatus(
        status=status_str,
        embedding_model_name="",
        db_dir="",
        k_matches=1,
        index_size=0,
    )


def _resolve_status(vector_store: VectorStoreManager) -> str:
    """Resolve the current vector store lifecycle status."""
    if vector_store.load_error is not None:
        return "error"

    if vector_store.ready_event.is_set() and vector_store.embed is not None:
        return "ready"

    return "loading"
