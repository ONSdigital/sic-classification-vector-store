"""Tests for the SIC API."""

import os
import subprocess

import pytest
import requests


class TestSicApi:
    """Test for the SIC API."""

    url_base = os.environ.get('SIC_API_URL')
    if url_base is None:
        raise ValueError("SIC_API_URL environment variable is not set.")
    else:
        print(f"SIC API URL to test: {url_base}")   

    id_token = os.environ.get('SA_ID_TOKEN')
    if id_token is None:
        raise ValueError("SA_ID_TOKEN environment variable is not set.")

    def test_sic_api_status(self) -> None:
        """Test SIC API returns successful /status response."""

        endpoint = f"{self.url_base}/status"

        response = requests.get(
            endpoint,
            headers={"Authorization": f"Bearer {self.id_token}"},
            timeout=30,
        )

        assert response.status_code == 200, (
            f"Expected status code 200, but got {response.status_code}."
        )

    def test_sic_api_search_index(self) -> None:
        """Test SIC API returns successful /search-index response."""

        endpoint = f"{self.url_base}/search-index"

        response = requests.post(
            endpoint,
            json={
                "industry_descr": "school teacher",
                "job_title": "teach maths",
                "job_description": "mainstream education",
            },
            headers={"Authorization": f"Bearer {self.id_token}"},
            timeout=30,
        )

        assert response.status_code == 200, (
            f"Expected status code 200, but got {response.status_code}."
        )