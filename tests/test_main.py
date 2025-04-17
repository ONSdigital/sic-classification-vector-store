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

import logging
import time
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from api.main import app  # Adjust the import based on your project structure

logger = logging.getLogger(__name__)
client = TestClient(app)  # Create a test client for your FastAPI app

MAX_WAIT_TIME = 8 * 60  # 8 minutes in seconds
POLL_INTERVAL = 10  # Poll every 10 seconds


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
def test_get_config():
    """Test the `/v1/sic-vector-store/status` endpoint.

    This test verifies that the endpoint returns a successful HTTP status code
    and that the response JSON contains the expected configuration for the
    `llm_model` key.

    Assertions:
    - The response status code is HTTPStatus.OK.
    - The `llm_model` in the response JSON is set to "gpt-4".
    """
    response = client.get("/v1/sic-vector-store/status")

    # The vector store is not ready yet, so we expect the status to
    # be "loading" and all fileds to be "unknown"
    assert response.status_code == HTTPStatus.OK
    assert response.json()["status"] == "loading"
    assert response.json()["llm_model_name"] == "unknown"
    assert response.json()["embedding_model_name"] == "unknown"
    assert response.json()["db_dir"] == "unknown"
    assert response.json()["sic_index_file"] == "unknown"
    assert response.json()["sic_structure_file"] == "unknown"
    assert response.json()["sic_condensed_file"] == "unknown"
    assert response.json()["matches"] == 0
    assert response.json()["index_size"] == 0


@pytest.mark.api
def test_status_ready():
    """Test the `/v1/sic-vector-store/status` endpoint until the status is ready.

    This test periodically checks the status endpoint to wait for the vector store
    to be ready. If the status does not become "ready" within 8 minutes, the test fails.
    Once the status is "ready", it verifies that the returned values are not "unknown" or 0.

    Assertions:
    - The response status code is HTTPStatus.OK.
    - The `status` in the response JSON is "ready".
    - None of the fields (`llm_model_name`, `embedding_model_name`, etc.) are "unknown".
    - Numeric fields (`matches`, `index_size`) are greater than 0.
    """
    # The 'with' allows the vector store thread to run in the TestClient
    with TestClient(app) as client:  # pylint: disable=redefined-outer-name
        start_time = time.time()

        while True:
            response = client.get("/v1/sic-vector-store/status")
            assert response.status_code == HTTPStatus.OK

            data = response.json()
            if data["status"] == "ready":
                # Verify that none of the fields are "unknown" or 0
                assert data["llm_model_name"] != "unknown"
                assert data["embedding_model_name"] != "unknown"
                assert data["db_dir"] != "unknown"
                assert data["sic_index_file"] != "unknown"
                assert data["sic_structure_file"] != "unknown"
                assert data["sic_condensed_file"] != "unknown"
                assert data["matches"] > 0
                assert data["index_size"] > 0
                break

            # Check if the maximum wait time has been exceeded
            elapsed_time = time.time() - start_time
            if elapsed_time > MAX_WAIT_TIME:
                pytest.fail("The vector store did not become ready within 8 minutes.")

            # Wait before polling again
            time.sleep(POLL_INTERVAL)
