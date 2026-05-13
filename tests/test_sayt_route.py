"""Tests for the SIC vector-store SAYT endpoint."""

from collections.abc import Generator
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from sic_classification_vector_store.api.main import app, lifespan
from sic_classification_vector_store.api.routes.v1.sayt import get_sayt_manager

pytestmark = pytest.mark.api


@pytest.fixture(autouse=True)
def clear_dependency_overrides() -> Generator[None, None, None]:
    """Ensure dependency overrides do not leak between route tests."""
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def _setup_sayt_override(mock_manager) -> None:
    """Override the route dependency with a supplied SAYT manager."""
    app.dependency_overrides[get_sayt_manager] = lambda: mock_manager


@pytest.mark.asyncio
async def test_lifespan_yields_sayt_manager_in_state(mocker) -> None:
    """The app lifespan should share the warmed manager through request state."""
    mock_manager = MagicMock()
    mocker.patch(
        "sic_classification_vector_store.api.main.SaytManager",
        return_value=mock_manager,
    )
    mock_start = mocker.patch("sic_classification_vector_store.api.main.Thread.start")

    async with lifespan(app) as state:
        assert state == {"sayt_manager": mock_manager}

    assert mock_start.call_count == 2  # noqa: PLR2004


def test_get_sayt_manager_reads_from_request_state() -> None:
    """The route dependency should read the warmed manager from request state."""
    mock_manager = MagicMock()
    request = MagicMock()
    request.state.sayt_manager = mock_manager

    assert get_sayt_manager(request) is mock_manager


def test_sayt_endpoint_returns_suggestions() -> None:
    """The route should return suggester results from the service layer."""
    mock_manager = MagicMock()
    mock_manager.suggest.return_value = [
        "Street lighting installation",
        "Insulating activities",
    ]
    _setup_sayt_override(mock_manager)
    client = TestClient(app)

    response = client.get(
        "/v1/sic-vector-store/sayt",
        params={"description": "street", "num_suggestions": "2"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "suggestions": ["Street lighting installation", "Insulating activities"]
    }
    mock_manager.suggest.assert_called_once_with("street", 2)


def test_sayt_endpoint_returns_service_unavailable() -> None:
    """The route should surface manager readiness failures as 503 responses."""
    mock_manager = MagicMock()
    mock_manager.suggest.side_effect = RuntimeError("SAYT suggester is not ready")
    _setup_sayt_override(mock_manager)
    client = TestClient(app)

    response = client.get(
        "/v1/sic-vector-store/sayt",
        params={"description": "street"},
    )

    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert response.json() == {"detail": "SAYT suggester is not ready"}


def test_sayt_endpoint_returns_internal_server_error() -> None:
    """The route should wrap unexpected suggester errors as 500 responses."""
    mock_manager = MagicMock()
    mock_manager.suggest.side_effect = ValueError("boom")
    _setup_sayt_override(mock_manager)
    client = TestClient(app)

    response = client.get(
        "/v1/sic-vector-store/sayt",
        params={"description": "street"},
    )

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.json() == {"detail": "Error retrieving SIC SAYT suggestions: boom"}
    mock_manager.suggest.assert_called_once_with("street", None)


def test_sayt_endpoint_rejects_empty_description() -> None:
    """The route should reject empty descriptions."""
    mock_manager = MagicMock()
    _setup_sayt_override(mock_manager)
    client = TestClient(app)

    response = client.get(
        "/v1/sic-vector-store/sayt",
        params={"description": ""},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"detail": "Description cannot be empty"}
