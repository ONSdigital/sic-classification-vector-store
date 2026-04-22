"""Unit tests for the status route helpers."""

from threading import Event
from typing import Any, cast

from sic_classification_vector_store.api.routes.v1.status import (
    _resolve_file_source,
    _resolve_status,
)
from sic_classification_vector_store.utils.vector_store import VectorStoreManager


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


def test_resolve_file_source_parses_tuple_string() -> None:
    """Tuple-like strings should be converted into structured file sources."""
    result = _resolve_file_source(
        "('sic_classification_vector_store.data.sic_index', 'uksic2007indexeswithaddendumdecember2022.xlsx')"
    )

    assert result.package == "sic_classification_vector_store.data.sic_index"
    assert result.file == "uksic2007indexeswithaddendumdecember2022.xlsx"


def test_resolve_file_source_parses_tuple_value() -> None:
    """Tuple values should be converted into structured file sources."""
    result = _resolve_file_source(
        (
            "sic_classification_vector_store.data.sic_index",
            "uksic2007indexeswithaddendumdecember2022.xlsx",
        )
    )

    assert result.package == "sic_classification_vector_store.data.sic_index"
    assert result.file == "uksic2007indexeswithaddendumdecember2022.xlsx"


def test_resolve_file_source_falls_back_to_raw_string() -> None:
    """Non-tuple strings should be returned as raw file values."""
    result = _resolve_file_source("not-a-tuple")

    assert result.package == "unknown"
    assert result.file == "not-a-tuple"
