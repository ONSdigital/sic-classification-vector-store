"""This module contains test cases for the Vectore Store API using FastAPI's TestClient.

Functions:
    test_read_root():
        Tests the root endpoint ("/") of the API to ensure it returns a 200 OK status
        and the expected JSON response indicating the API is running.

    test_get_config():
        Tests the "/v1/sic-vector-store/config" endpoint to ensure it returns a 200 OK status
        and verifies that the configuration includes the expected LLM model.

Dependencies:
    - pytest: Used for marking and running test cases.
    - fastapi.testclient.TestClient: Used to simulate HTTP requests to the FastAPI app.
    - http.HTTPStatus: Provides standard HTTP status codes for assertions.
"""

import os
import time
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from survey_assist_utils.logging import get_logger

import sic_classification_vector_store.utils.vector_store as vs_module
from sic_classification_vector_store.api.main import (
    app,  # Adjust the import based on your project structure
)
from sic_classification_vector_store.utils.build_vector_store_index import (
    build_vector_store_index,
)

logger = get_logger(__name__)
client = TestClient(app)  # Create a test client for your FastAPI app

MAX_WAIT_TIME = 8 * 60  # 8 minutes in seconds
POLL_INTERVAL = 10  # Poll every 10 seconds
STATUS_RESPONSE_KEYS = {
    "status",
    "embedding_model_name",
    "embedding_backend",
    "db_dir",
    "index_source_file",
    "k_matches",
    "index_size",
}


@pytest.mark.api
def test_read_root():
    """Test the root endpoint of the API.

    This test sends a GET request to the root endpoint ("/") and verifies:
    1. The response status code is HTTP 200 (OK).
    2. The response JSON contains the expected message indicating the API is running.
    """
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "SIC Vector Store API is running"}


@pytest.mark.api
def test_get_status_loading():
    """Test the `/v1/sic-vector-store/status` endpoint.

    This test verifies that the endpoint returns a successful HTTP status code
    and that the response JSON matches the loading-state API contract.

    Assertions:
    - The response status code is HTTPStatus.OK.
    - The `status` in the response JSON is set to "loading".
    """
    response = client.get("/v1/sic-vector-store/status")
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert data["status"] == "loading"
    assert set(data) == STATUS_RESPONSE_KEYS


@pytest.mark.api
def test_status_ready(monkeypatch, tmp_path):
    """Test the `/v1/sic-vector-store/status` endpoint until the status is ready.

    This test periodically checks the status endpoint to wait for the vector store
    to be ready. If the status does not become "ready" within 8 minutes, the test fails.
    Once the status is "ready", it verifies that the returned values are not "unknown" or 0.

    Assertions:
    - The response status code is HTTPStatus.OK.
    - The `status` in the response JSON is "ready".
    - None of the status fields are "unknown".
    - Numeric fields (`k_matches`, `index_size`) are greater than 0.
    """
    example_csv = os.path.join(os.path.dirname(__file__), "data", "example.csv")
    build_vector_store_index(db_dir=str(tmp_path), index_source_file=example_csv)
    monkeypatch.setattr(vs_module, "VECTOR_STORE_DIR", str(tmp_path))
    # The 'with' allows the vector store thread to run in the TestClient
    with TestClient(app) as client:  # pylint: disable=redefined-outer-name
        start_time = time.time()

        while True:
            response = client.get("/v1/sic-vector-store/status")
            assert response.status_code == HTTPStatus.OK

            data = response.json()
            if data["status"] == "error":
                pytest.fail("The vector store reported an error during startup.")

            if data["status"] == "ready":
                assert set(data) == STATUS_RESPONSE_KEYS
                assert data["db_dir"] not in ["unknown", "", None]
                assert data["embedding_model_name"] not in ["unknown", "", None]
                assert data["k_matches"] > 0
                assert data["index_size"] > 0
                break

            # Check if the maximum wait time has been exceeded
            elapsed_time = time.time() - start_time
            if elapsed_time > MAX_WAIT_TIME:
                pytest.fail("The vector store did not become ready within 8 minutes.")

            # Wait before polling again
            time.sleep(POLL_INTERVAL)
