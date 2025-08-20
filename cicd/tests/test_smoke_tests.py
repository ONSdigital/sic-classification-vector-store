"""Tests for the SIC API."""

import os
import subprocess

import pytest
import requests


@pytest.fixture
def id_token():
    """Fixture to generate an ID token for the SIC API."""

    gcloud_print_id_token = subprocess.check_output(
        ["gcloud", "auth", "print-identity-token"]  # noqa: S607
    )
    id_token = gcloud_print_id_token.decode().strip()
    return id_token


class TestSicApi:
    """Test for the SIC API."""

    url_base = os.environ.get('SIC_API_URL')
    if url_base is None:
        raise ValueError("SIC_API_URL environment variable is not set.")
    else:
        print(f"SIC API URL to test: {url_base}")   

    def test_sic_api_status(self, id_token) -> None:
        """Test SIC API returns successful /status response."""

        endpoint = f"{self.url_base}/status"

        response = requests.get(
            endpoint,
            headers={"Authorization": f"Bearer {id_token}"},
            timeout=30,
        )

        assert response.status_code == 200, (
            f"Expected status code 200, but got {response.status_code}."
        )

    def test_sic_api_search_index(self, id_token) -> None:
        """Test SIC API returns successful /search-index response."""

        endpoint = f"{self.url_base}/search-index"

        response = requests.post(
            endpoint,
            json={
                "industry_descr": "school teacher",
                "job_title": "teach maths",
                "job_description": "mainstream education",
            },
            headers={"Authorization": f"Bearer {id_token}"},
            timeout=30,
        )

        assert response.status_code == 200, (
            f"Expected status code 200, but got {response.status_code}."
        )