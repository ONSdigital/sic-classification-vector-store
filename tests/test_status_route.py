"""Unit tests for the status route helpers."""

from sic_classification_vector_store.api.routes.v1.status import _resolve_file_source


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
