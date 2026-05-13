"""Shared FastAPI dependencies for SIC vector-store routes."""

from typing import cast

from fastapi import Request

from sic_classification_vector_store.utils.sayt import SaytManager
from sic_classification_vector_store.utils.vector_store import (
    VectorStoreManager,
    vector_store_manager,
)


def get_vector_store() -> VectorStoreManager:
    """Get the shared vector-store manager."""
    return vector_store_manager


def get_sayt_manager(request: Request) -> SaytManager:
    """Get the warmed SAYT manager from FastAPI request state."""
    return cast(SaytManager, request.state.sayt_manager)
