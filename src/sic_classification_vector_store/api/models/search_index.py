"""This module contains the models for the status response.

The models in this module are used to represent the response
returned by the API.
"""

from pydantic import BaseModel


class SearchIndexRequest(BaseModel):
    """Model representing a request to the vector store search index."""

    industry_descr: str
    job_title: str
    job_description: str
