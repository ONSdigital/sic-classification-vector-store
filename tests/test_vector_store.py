"""Module that provides test functions for the SIC Vector Store and API.

Unit tests for endpoints and utility functions in the vector store.
"""

import pytest

from sic_classification_vector_store.utils.vector_store import VectorStoreManager


@pytest.mark.utils
def test_vector_store_manager_load(mocker):
    """Test VectorStoreManager.load creates the EmbeddingHandler and fetches config."""
    mock_embed_handler = mocker.patch(
        "sic_classification_vector_store.utils.vector_store.EmbeddingHandler"
    )
    mock_embed_instance = mock_embed_handler.return_value
    mock_embed_instance.get_embed_config.return_value = {"status": "mocked"}

    manager = VectorStoreManager()
    manager.load()

    mock_embed_handler.assert_called_once_with(
        db_dir="src/sic_classification_vector_store/data/vector_store",
        index_source_file=None,
    )
    mock_embed_instance.get_embed_config.assert_called_once()
    assert manager.embed == mock_embed_instance
    assert manager.status == {"status": "mocked"}
