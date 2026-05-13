"""Unit tests for the status route helpers."""

from threading import Event
from typing import Any, cast

import pytest

from sic_classification_vector_store.api.models.status import StatusResponse
from sic_classification_vector_store.api.routes.v1.status import (
    _resolve_status,
    get_status,
    get_vector_store,
)
from sic_classification_vector_store.utils.vector_store import (
    VectorStoreManager,
)
from sic_classification_vector_store.utils.vector_store import (
    vector_store_manager as singleton_vector_store_manager,
)


def _make_vector_store_manager(
    *, ready: bool, embed: object | None = None, load_error: str | None = None
) -> VectorStoreManager:
    """Build a vector store manager for status resolution tests."""
    vector_store_manager = VectorStoreManager()
    vector_store_manager.ready_event = Event()
    if ready:
        vector_store_manager.ready_event.set()
    vector_store_manager.embed = cast(Any, embed)
    vector_store_manager.load_error = load_error
    return vector_store_manager


def test_resolve_status_returns_loading_while_vector_store_initialises() -> None:
    """The status should remain loading until the embedder is ready."""
    vector_store_manager = _make_vector_store_manager(ready=False)

    assert _resolve_status(vector_store_manager) == "loading"


def test_resolve_status_returns_ready_after_successful_load() -> None:
    """The status should be ready once the embedder is available."""
    vector_store_manager = _make_vector_store_manager(ready=True, embed=object())

    assert _resolve_status(vector_store_manager) == "ready"


def test_resolve_status_returns_error_after_failed_load() -> None:
    """The status should surface startup failures instead of reporting ready."""
    vector_store_manager = _make_vector_store_manager(
        ready=True,
        load_error="failed to load vector store",
    )

    assert _resolve_status(vector_store_manager) == "error"


def test_get_vector_store_returns_singleton_manager() -> None:
    """The route dependency should expose the shared vector store manager."""
    assert get_vector_store() is singleton_vector_store_manager


@pytest.mark.asyncio
async def test_get_status_returns_status_response() -> None:
    """The status route should map the manager state into the response model."""
    expected_matches = 20
    expected_index_size = 16618

    vector_store_manager = _make_vector_store_manager(ready=True, embed=object())
    vector_store_manager.config_data = {
        "embedding_model_name": "all-MiniLM-L6-v2",
        "db_dir": "src/sic_classification_vector_store/data/vector_store",
        "index_source_file": "some_index_file.csv",
        "k_matches": expected_matches,
        "index_size": expected_index_size,
    }

    result = await get_status(vector_store_manager)

    assert isinstance(result, StatusResponse)
    assert result.status == "ready"
    assert result.embedding_model_name == "all-MiniLM-L6-v2"
    assert result.db_dir == "src/sic_classification_vector_store/data/vector_store"
    assert result.k_matches == expected_matches
    assert result.index_size == expected_index_size


