"""Module that provides test functions for the SIC Vector Store and API.

Unit tests for endpoints and utility functions in the vector store.
"""

import pytest

from utils.common import safe_int


# ruff: noqa: PLR2004
@pytest.mark.utils
def test_safe_int_valid():
    """Test safe_int with valid integer input."""
    assert safe_int(42) == 42
    assert safe_int("42") == 42


@pytest.mark.utils
def test_safe_int_invalid():
    """Test safe_int with invalid input."""
    assert safe_int("invalid", default=5) == 5
    assert safe_int(None, default=10) == 10


@pytest.mark.utils
def test_safe_int_default():
    """Test safe_int with default value."""
    assert safe_int("invalid") == 0
    assert safe_int(None) == 0
