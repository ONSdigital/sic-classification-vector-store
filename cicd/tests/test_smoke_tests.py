"""Tests for the SIC API."""

import os
import subprocess

import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


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

        print(f"Calling {endpoint}...")
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

        retry_strategy = Retry(
            total=5,  # maximum number of retries
            backoff_factor=7,
            status_forcelist=[503],  # the HTTP status codes to retry on
        )       

        # create an HTTP adapter with the retry strategy and mount it to the session
        adapter = HTTPAdapter(max_retries=retry_strategy)
        
        # create a new session object
        session = requests.Session()
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        endpoint = f"{self.url_base}/search-index"

        print(f"Calling {endpoint}, will retry upto 5 times (if a HTTP status 503 is returned) with an exponential backoff factor of 7...")
        response = session.post(
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