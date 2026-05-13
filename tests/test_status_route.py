"""Unit tests for the status route helpers."""

from threading import Event
from typing import Any, cast
from unittest.mock import MagicMock

import pytest

from sic_classification_vector_store.api.models.status import StatusResponse
from sic_classification_vector_store.api.routes.v1.status import (
    _resolve_file_source,
    _resolve_manager_status,
    get_sayt_manager,
    get_status,
    get_vector_store,
)
from sic_classification_vector_store.utils.sayt import SaytManager
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


def _make_sayt_manager(
    *, ready: bool, suggester: object | None = None, load_error: str | None = None
) -> SaytManager:
    """Build a SAYT manager for status resolution tests."""
    sayt_manager = SaytManager("/resolved/example_sic_lookup_data.csv")
    sayt_manager.ready_event = Event()
    if ready:
        sayt_manager.ready_event.set()
    sayt_manager.suggester = cast(Any, suggester)
    sayt_manager.load_error = load_error
    return sayt_manager


def test_resolve_status_returns_loading_while_vector_store_initialises() -> None:
    """The status should remain loading until the embedder is ready."""
    vector_store_manager = _make_vector_store_manager(ready=False)

    assert (
        _resolve_manager_status(
            is_ready=vector_store_manager.ready_event.is_set(),
            loaded_value=vector_store_manager.embed,
            load_error=vector_store_manager.load_error,
        )
        == "loading"
    )


def test_resolve_status_returns_ready_after_successful_load() -> None:
    """The status should be ready once the embedder is available."""
    vector_store_manager = _make_vector_store_manager(ready=True, embed=object())

    assert (
        _resolve_manager_status(
            is_ready=vector_store_manager.ready_event.is_set(),
            loaded_value=vector_store_manager.embed,
            load_error=vector_store_manager.load_error,
        )
        == "ready"
    )


def test_resolve_status_returns_error_after_failed_load() -> None:
    """The status should surface startup failures instead of reporting ready."""
    vector_store_manager = _make_vector_store_manager(
        ready=True,
        load_error="failed to load vector store",
    )

    assert (
        _resolve_manager_status(
            is_ready=vector_store_manager.ready_event.is_set(),
            loaded_value=vector_store_manager.embed,
            load_error=vector_store_manager.load_error,
        )
        == "error"
    )


def test_resolve_sayt_status_returns_loading_while_suggester_initialises() -> None:
    """The SAYT status should remain loading until the suggester is ready."""
    sayt_manager = _make_sayt_manager(ready=False)

    assert (
        _resolve_manager_status(
            is_ready=sayt_manager.ready_event.is_set(),
            loaded_value=sayt_manager.suggester,
            load_error=sayt_manager.load_error,
        )
        == "loading"
    )


def test_resolve_sayt_status_returns_ready_after_successful_load() -> None:
    """The SAYT status should be ready once the suggester is available."""
    sayt_manager = _make_sayt_manager(ready=True, suggester=object())

    assert (
        _resolve_manager_status(
            is_ready=sayt_manager.ready_event.is_set(),
            loaded_value=sayt_manager.suggester,
            load_error=sayt_manager.load_error,
        )
        == "ready"
    )


def test_resolve_sayt_status_returns_error_after_failed_load() -> None:
    """The SAYT status should surface startup failures instead of reporting ready."""
    sayt_manager = _make_sayt_manager(
        ready=True,
        load_error="failed to load sayt suggester",
    )

    assert (
        _resolve_manager_status(
            is_ready=sayt_manager.ready_event.is_set(),
            loaded_value=sayt_manager.suggester,
            load_error=sayt_manager.load_error,
        )
        == "error"
    )


def test_get_vector_store_returns_singleton_manager() -> None:
    """The route dependency should expose the shared vector store manager."""
    assert get_vector_store() is singleton_vector_store_manager


def test_get_sayt_manager_reads_from_request_state() -> None:
    """The route dependency should read the warmed SAYT manager from request state."""
    mock_manager = MagicMock()
    request = MagicMock()
    request.state.sayt_manager = mock_manager

    assert get_sayt_manager(request) is mock_manager


@pytest.mark.asyncio
async def test_get_status_returns_status_response() -> None:
    """The status route should map the manager state into the response model."""
    expected_matches = 20
    expected_index_size = 16618

    vector_store_manager = _make_vector_store_manager(ready=True, embed=object())
    sayt_manager = _make_sayt_manager(ready=True, suggester=object())
    vector_store_manager.status = {
        "embedding_model_name": "all-MiniLM-L6-v2",
        "db_dir": "src/sic_classification_vector_store/data/vector_store",
        "sic_index": (
            "sic_classification_vector_store.data.sic_index",
            "uksic2007indexeswithaddendumdecember2022.xlsx",
        ),
        "sic_structure": (
            "sic_classification_vector_store.data.sic_index",
            "publisheduksicsummaryofstructureworksheet.xlsx",
        ),
        "sic_condensed": (
            "industrial_classification_utils.data.example",
            "sic_2d_condensed.txt",
        ),
        "matches": expected_matches,
        "index_size": expected_index_size,
    }

    result = await get_status(vector_store_manager, sayt_manager)

    assert isinstance(result, StatusResponse)
    assert result.vector_store_status == "ready"
    assert result.sayt_status == "ready"
    assert result.embedding_model_name == "all-MiniLM-L6-v2"
    assert result.db_dir == "src/sic_classification_vector_store/data/vector_store"
    assert (
        result.sic_index_source.package
        == "sic_classification_vector_store.data.sic_index"
    )
    assert (
        result.sic_index_source.file == "uksic2007indexeswithaddendumdecember2022.xlsx"
    )
    assert (
        result.sic_structure_source.package
        == "sic_classification_vector_store.data.sic_index"
    )
    assert (
        result.sic_structure_source.file
        == "publisheduksicsummaryofstructureworksheet.xlsx"
    )
    assert (
        result.sic_condensed_source.package
        == "industrial_classification_utils.data.example"
    )
    assert result.sic_condensed_source.file == "sic_2d_condensed.txt"
    assert result.matches == expected_matches
    assert result.index_size == expected_index_size


def test_resolve_file_source_parses_tuple_string() -> None:
    """Tuple-like strings should be converted into structured file sources."""
    result = _resolve_file_source(
        "('sic_classification_vector_store.data.sic_index', "
        "'uksic2007indexeswithaddendumdecember2022.xlsx')"
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


def test_resolve_file_source_falls_back_to_original_string_after_parsing() -> None:
    """Parsed non-tuple string values should still return the original raw string."""
    result = _resolve_file_source("['not', 'a', 'tuple']")

    assert result.package == "unknown"
    assert result.file == "['not', 'a', 'tuple']"


def test_resolve_file_source_returns_unknown_for_unusable_tuple_value() -> None:
    """Tuple values with the wrong shape should return the unknown fallback."""
    result = _resolve_file_source(("too", "many", "values"))

    assert result.package == "unknown"
    assert result.file == "unknown"
