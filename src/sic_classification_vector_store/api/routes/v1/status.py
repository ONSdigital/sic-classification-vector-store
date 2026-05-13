"""Module that provides the configuration endpoint for the Survey Assist API.

This module contains the configuration endpoint for the Survey Assist API.
It defines the configuration endpoint and returns the current configuration settings.
"""

from ast import literal_eval
from typing import Annotated

from fastapi import APIRouter, Depends

from sic_classification_vector_store.api.deps import get_sayt_manager, get_vector_store
from sic_classification_vector_store.api.models.status import (
    FileSource,
    RuntimeStatus,
    StatusResponse,
)
from sic_classification_vector_store.utils.common import safe_int
from sic_classification_vector_store.utils.sayt import SaytManager
from sic_classification_vector_store.utils.vector_store import VectorStoreManager

router = APIRouter(tags=["Status"])


@router.get("/status", response_model=StatusResponse)
async def get_status(
    vector_store: Annotated[VectorStoreManager, Depends(get_vector_store)],
    sayt_manager: Annotated[SaytManager, Depends(get_sayt_manager)],
) -> StatusResponse:
    """Get the current status of the vector store.

    Args:
        vector_store: Vector store manager instance
        sayt_manager: SIC SAYT manager instance

    Returns:
        StatusResponse: A dictionary containing the current status.
    """
    return StatusResponse(
        vector_store_status=_resolve_manager_status(
            is_ready=vector_store.ready_event.is_set(),
            loaded_value=vector_store.embed,
            load_error=vector_store.load_error,
        ),
        sayt_status=_resolve_manager_status(
            is_ready=sayt_manager.ready_event.is_set(),
            loaded_value=sayt_manager.suggester,
            load_error=sayt_manager.load_error,
        ),
        embedding_model_name=str(vector_store.status.get("embedding_model_name", "")),
        db_dir=str(vector_store.status.get("db_dir", "")),
        sic_index_source=_resolve_file_source(vector_store.status.get("sic_index", "")),
        sic_structure_source=_resolve_file_source(
            vector_store.status.get("sic_structure", "")
        ),
        sic_condensed_source=_resolve_file_source(
            vector_store.status.get("sic_condensed", "")
        ),
        matches=safe_int(vector_store.status.get("matches", 0)),
        index_size=safe_int(vector_store.status.get("index_size", 0)),
    )


def _resolve_manager_status(
    *, is_ready: bool, loaded_value: object | None, load_error: str | None
) -> RuntimeStatus:
    """Resolve the shared lifecycle status for a managed component."""
    if load_error is not None:
        return RuntimeStatus.ERROR

    if is_ready and loaded_value is not None:
        return RuntimeStatus.READY

    return RuntimeStatus.LOADING


def _resolve_file_source(vector_store_status: object) -> FileSource:
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
