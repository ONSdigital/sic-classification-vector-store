"""Module that provides the configuration endpoint for the Survey Assist API.

This module contains the configuration endpoint for the Survey Assist API.
It defines the configuration endpoint and returns the current configuration settings.
"""

from ast import literal_eval
from typing import Annotated

from fastapi import APIRouter, Depends

from sic_classification_vector_store.api.models.status import FileSource, StatusResponse
from sic_classification_vector_store.utils.common import safe_int
from sic_classification_vector_store.utils.vector_store import VectorStoreManager, vector_store_manager

router = APIRouter(tags=["Status"])


def get_vector_store():
    """Get a vector store instance.

    Returns:
        VectorStoreManager: A vector store manager instance.
    """
    return vector_store_manager


@router.get("/status", response_model=StatusResponse)
async def get_status(vector_store: Annotated[VectorStoreManager, Depends(get_vector_store)]) -> StatusResponse:
    """Get the current status of the vector store.

    Args:
        vector_store: Vector store manager instance

    Returns:
        StatusResponse: A dictionary containing the current status.
    """
    status_resp = StatusResponse(
        status=_resolve_status(vector_store),
        embedding_model_name=str(vector_store.status.get("embedding_model_name", "")),
        db_dir=str(vector_store.status.get("db_dir", "")),
        sic_index_source=_resolve_file_source(vector_store.status.get("sic_index", "")),
        sic_structure_source=_resolve_file_source(vector_store.status.get("sic_structure", "")),
        sic_condensed_source=_resolve_file_source(vector_store.status.get("sic_condensed", "")),
        matches=safe_int(vector_store.status.get("matches", 0)),
        index_size=safe_int(vector_store.status.get("index_size", 0)),
    )
    return status_resp


def _resolve_status(vector_store: VectorStoreManager) -> str:
    """Resolve the current vector store lifecycle status."""
    if vector_store.load_error is not None:
        return "error"

    if vector_store.ready_event.is_set() and vector_store.embed is not None:
        return "ready"

    return "loading"


def _resolve_file_source(vector_store_status: tuple | str) -> FileSource:
    """Resolve a file source from the vector store status."""
    raw_status = vector_store_status if isinstance(vector_store_status, str) else None

    if raw_status is not None:
        try:
            vector_store_status = literal_eval(raw_status)
        except (SyntaxError, ValueError):
            return FileSource(package="unknown", file=raw_status)

    if isinstance(vector_store_status, tuple):
        try:
            package, file = vector_store_status
        except ValueError:
            pass
        else:
            return FileSource(package=str(package), file=str(file))

    if raw_status is not None:
        return FileSource(package="unknown", file=raw_status)

    return FileSource(package="unknown", file="unknown")
