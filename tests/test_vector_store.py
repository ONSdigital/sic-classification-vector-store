"""Module that provides test functions for the SIC Vector Store and API.

Unit tests for endpoints and utility functions in the vector store.
"""

import pytest

from sic_classification_vector_store.utils.vector_store import load_vector_store


@pytest.mark.utils
def test_load_vector_store(mocker):
    """Test the load_vector_store function."""
    mock_embed_handler = mocker.patch(
        "sic_classification_vector_store.utils.vector_store.EmbeddingHandler"
    )
    mock_embed_instance = mock_embed_handler.return_value
    mock_embed_instance.get_embed_config.return_value = {"status": "mocked"}

    embed = load_vector_store()

    mock_embed_handler.assert_called_once_with(
        db_dir="src/sic_classification_vector_store/data/vector_store"
    )
    mock_embed_instance.embed_index.assert_called_once()
    assert embed == mock_embed_instance
