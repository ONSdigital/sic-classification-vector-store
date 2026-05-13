"""Unit tests for the SIC SAYT manager."""

from contextlib import nullcontext
from pathlib import Path

import pytest

from sic_classification_vector_store.utils.sayt import SaytManager

pytestmark = pytest.mark.utils


def test_load_uses_env_override_when_configured(mocker, monkeypatch) -> None:
    """The manager should prefer an environment override when no path is supplied."""
    monkeypatch.setenv("SIC_LOOKUP_DATA_PATH", "  /configured/sayt.csv  ")
    mock_files = mocker.patch(
        "sic_classification_vector_store.utils.sayt.resources.files"
    )
    mock_from_csv = mocker.patch(
        "sic_classification_vector_store.utils.sayt.SAYTSuggester.from_csv"
    )

    manager = SaytManager()

    manager.load()

    mock_files.assert_not_called()
    mock_from_csv.assert_called_once_with(
        "/configured/sayt.csv",
        search_text_col="description",
        display_text_col="description",
    )


def test_load_uses_packaged_data_when_available(mocker, tmp_path, monkeypatch) -> None:
    """The manager should fall back to packaged data when no override is supplied."""
    packaged_data_dir = tmp_path / "package" / "data"
    packaged_data_dir.mkdir(parents=True)
    expected_path = packaged_data_dir / "example_sic_lookup_data.csv"
    expected_path.write_text("description\nStreet lighting installation\n")
    monkeypatch.delenv("SIC_LOOKUP_DATA_PATH", raising=False)

    mocker.patch(
        "sic_classification_vector_store.utils.sayt.resources.files",
        return_value=packaged_data_dir,
    )
    mocker.patch(
        "sic_classification_vector_store.utils.sayt.resources.as_file",
        return_value=nullcontext(expected_path),
    )
    mock_info = mocker.patch("sic_classification_vector_store.utils.sayt.logger.info")
    mock_from_csv = mocker.patch(
        "sic_classification_vector_store.utils.sayt.SAYTSuggester.from_csv"
    )

    manager = SaytManager()

    manager.load()

    mock_from_csv.assert_called_once_with(
        expected_path,
        search_text_col="description",
        display_text_col="description",
    )
    mock_info.assert_any_call(
        "Using packaged SIC SAYT data",
        data_path=str(expected_path),
    )


def test_load_raises_when_packaged_data_is_unavailable(mocker, monkeypatch) -> None:
    """The manager should fail with a clear override message."""
    monkeypatch.delenv("SIC_LOOKUP_DATA_PATH", raising=False)
    mocker.patch(
        "sic_classification_vector_store.utils.sayt.resources.files",
        side_effect=ImportError("packaged data unavailable"),
    )
    mock_warning = mocker.patch(
        "sic_classification_vector_store.utils.sayt.logger.warning"
    )
    message = (
        "Could not resolve packaged SIC SAYT data. "
        "Set SIC_LOOKUP_DATA_PATH to override the CSV path."
    )
    manager = SaytManager()

    with pytest.raises(RuntimeError, match=message):
        manager.load()

    mock_warning.assert_called_once_with(
        message,
        error="packaged data unavailable",
    )


def test_load_raises_when_packaged_file_is_missing(mocker, monkeypatch) -> None:
    """The manager should fail when the packaged CSV resource is missing."""
    packaged_data_dir = Path("/package/data")
    expected_path = packaged_data_dir / "example_sic_lookup_data.csv"
    monkeypatch.delenv("SIC_LOOKUP_DATA_PATH", raising=False)
    mocker.patch(
        "sic_classification_vector_store.utils.sayt.resources.files",
        return_value=packaged_data_dir,
    )
    mock_warning = mocker.patch(
        "sic_classification_vector_store.utils.sayt.logger.warning"
    )
    message = (
        "Packaged SIC SAYT data not found. "
        "Set SIC_LOOKUP_DATA_PATH to override the CSV path."
    )
    manager = SaytManager()

    with pytest.raises(RuntimeError, match=message):
        manager.load()

    mock_warning.assert_called_once_with(message, data_path=str(expected_path))


def test_load_builds_suggester(mocker) -> None:
    """The manager should build the SAYT suggester from the resolved CSV path."""
    expected_path = "/resolved/example_sic_lookup_data.csv"
    mocker.patch(
        "sic_classification_vector_store.utils.sayt.resources.files",
        return_value=Path("/package/data"),
    )
    mock_is_file = mocker.patch(
        "pathlib.Path.is_file",
        return_value=True,
    )
    mocker.patch(
        "sic_classification_vector_store.utils.sayt.resources.as_file",
        return_value=nullcontext(Path(expected_path)),
    )
    mock_from_csv = mocker.patch(
        "sic_classification_vector_store.utils.sayt.SAYTSuggester.from_csv"
    )

    manager = SaytManager()

    manager.load()

    mock_is_file.assert_called_once_with()
    mock_from_csv.assert_called_once_with(
        Path(expected_path),
        search_text_col="description",
        display_text_col="description",
    )


def test_load_prefers_explicit_data_path_over_packaged_resource(mocker) -> None:
    """An explicit data path should bypass packaged-resource resolution."""
    mock_files = mocker.patch(
        "sic_classification_vector_store.utils.sayt.resources.files"
    )
    mock_from_csv = mocker.patch(
        "sic_classification_vector_store.utils.sayt.SAYTSuggester.from_csv"
    )
    manager = SaytManager("/configured/sayt.csv")

    manager.load()

    mock_files.assert_not_called()
    mock_from_csv.assert_called_once_with(
        "/configured/sayt.csv",
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
