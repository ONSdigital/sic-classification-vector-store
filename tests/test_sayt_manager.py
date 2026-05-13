"""Unit tests for the SIC SAYT manager."""

from pathlib import Path

import pytest

from sic_classification_vector_store.utils.sayt import (
    SaytManager,
    resolve_sayt_data_path,
)

pytestmark = pytest.mark.utils


def test_resolve_sayt_data_path_prefers_env_var(monkeypatch) -> None:
    """The resolver should prefer a non-empty environment override."""
    monkeypatch.setenv("SIC_LOOKUP_DATA_PATH", "  /configured/sayt.csv  ")

    assert resolve_sayt_data_path() == "/configured/sayt.csv"


def test_resolve_sayt_data_path_uses_packaged_data_when_available(
    mocker, monkeypatch
) -> None:
    """The resolver should return the packaged CSV path when it is available."""
    packaged_data_dir = Path("/package/data")
    monkeypatch.delenv("SIC_LOOKUP_DATA_PATH", raising=False)
    mocker.patch(
        "sic_classification_vector_store.utils.sayt.resources.files",
        return_value=packaged_data_dir,
    )
    mock_info = mocker.patch("sic_classification_vector_store.utils.sayt.logger.info")

    assert resolve_sayt_data_path() == "/package/data/example_sic_lookup_data.csv"
    mock_info.assert_called_once_with(
        "Using packaged SIC SAYT data",
        data_path="/package/data/example_sic_lookup_data.csv",
    )


def test_resolve_sayt_data_path_falls_back_when_packaged_data_is_unavailable(
    mocker, monkeypatch
) -> None:
    """The resolver should fall back to the known site-packages path."""
    fallback_path = (
        "/usr/local/lib/python3.12/site-packages/industrial_classification/data/"
        "example_sic_lookup_data.csv"
    )
    monkeypatch.delenv("SIC_LOOKUP_DATA_PATH", raising=False)
    mocker.patch(
        "sic_classification_vector_store.utils.sayt.resources.files",
        side_effect=ImportError("packaged data unavailable"),
    )
    mock_warning = mocker.patch(
        "sic_classification_vector_store.utils.sayt.logger.warning"
    )

    assert resolve_sayt_data_path() == fallback_path
    mock_warning.assert_called_once_with(
        "Could not resolve packaged SIC SAYT data, using fallback",
        data_path=fallback_path,
        error="packaged data unavailable",
    )


def test_load_builds_suggester(mocker) -> None:
    """The manager should build the SAYT suggester from the resolved CSV path."""
    expected_path = "/resolved/example_sic_lookup_data.csv"
    mock_resolve = mocker.patch(
        "sic_classification_vector_store.utils.sayt.resolve_sayt_data_path",
        return_value=expected_path,
    )
    mock_from_csv = mocker.patch(
        "sic_classification_vector_store.utils.sayt.SAYTSuggester.from_csv"
    )

    manager = SaytManager()

    manager.load()

    mock_resolve.assert_called_once_with()
    mock_from_csv.assert_called_once_with(
        expected_path,
        search_text_col="description",
        display_text_col="description",
    )


def test_suggest_requires_ready_manager() -> None:
    """The manager should reject requests until the suggester is ready."""
    manager = SaytManager("/resolved/example_sic_lookup_data.csv")

    try:
        manager.suggest("street")
    except RuntimeError as exc:
        assert str(exc) == "SAYT suggester is not ready"
    else:
        raise AssertionError("Expected RuntimeError when SAYT manager is not ready")


def test_suggest_surfaces_load_error() -> None:
    """The manager should surface startup failures before serving suggestions."""
    manager = SaytManager("/resolved/example_sic_lookup_data.csv")
    manager.load_error = "csv missing"

    with pytest.raises(
        RuntimeError, match="SAYT suggester failed to load: csv missing"
    ):
        manager.suggest("street")


def test_suggest_requires_loaded_suggester_when_ready() -> None:
    """The manager should reject requests if readiness is set without a suggester."""
    manager = SaytManager("/resolved/example_sic_lookup_data.csv")
    manager.ready_event.set()

    with pytest.raises(RuntimeError, match="SAYT suggester not loaded"):
        manager.suggest("street")


def test_suggest_uses_loaded_suggester(mocker) -> None:
    """The manager should delegate suggestions to the warmed suggester."""
    manager = SaytManager("/resolved/example_sic_lookup_data.csv")
    manager.ready_event.set()
    mock_suggester = mocker.Mock()
    mock_suggester.suggest.return_value = ["Street lighting installation"]
    manager.suggester = mock_suggester

    result = manager.suggest("street", 2)

    assert result == ["Street lighting installation"]
    mock_suggester.suggest.assert_called_once_with("street", 2)


def test_sayt_manager_normalises_path_objects() -> None:
    """The manager should normalise path-like input."""
    manager = SaytManager(Path("/resolved/example_sic_lookup_data.csv"))

    assert manager.data_path == "/resolved/example_sic_lookup_data.csv"
