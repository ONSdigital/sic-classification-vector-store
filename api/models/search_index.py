"""This module contains the models for the status response.

The models in this module are used to represent the response
returned by the API.
"""

from pydantic import BaseModel, RootModel


class SearchIndexRequest(BaseModel):
    """Model representing a request to the vector store search index."""

    industry_descr: str
    job_title: str
    job_description: str


class SearchIndexItem(BaseModel):
    """Model representing an item in the vector store search index.

    Attributes:
        distance (float): vector search distance.
        title (str): sic title description.
        code (str): sic code.
        four_digit_code (str): four digit sic code.
        two_digit_code (str): two digit sic code.
    """

    distance: float
    title: str
    code: str
    four_digit_code: str
    two_digit_code: str


class SearchIndexResponse(
    RootModel[list[SearchIndexItem]]
):  # pylint: disable=too-few-public-methods
    """Model representing the vector store search index multi response."""

    pass  # pylint: disable=unnecessary-pass
