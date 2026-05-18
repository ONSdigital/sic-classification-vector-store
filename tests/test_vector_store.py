"""Module that provides test functions for the SIC Vector Store and API.

Unit tests for endpoints and utility functions in the vector store.
"""

import pytest

import sic_classification_vector_store.utils.vector_store as vs_module
from industrial_classification_utils.models.config_model import EmbeddingConfig
from sic_classification_vector_store.utils.vector_store import VectorStoreManager


@pytest.mark.utils
def test_vector_store_manager_load(mocker, monkeypatch, tmp_path):
    """Test VectorStoreManager.load creates the EmbeddingHandler and fetches config."""
    monkeypatch.setattr(vs_module, "VECTOR_STORE_DIR", str(tmp_path))

    mock_embed_handler = mocker.patch(
        "sic_classification_vector_store.utils.vector_store.EmbeddingHandler"
    )
    mock_embed_instance = mock_embed_handler.return_value
    mock_embed_instance.get_embed_config.return_value = EmbeddingConfig(
        embedding_model_name="mocked",
        db_dir=str(tmp_path),
        index_source_file="mocked",
        k_matches=10,
    )

    manager = VectorStoreManager()
    manager.load()

    mock_embed_handler.assert_called_once_with(
        db_dir=str(tmp_path),
    )
    mock_embed_instance.get_embed_config.assert_not_called()  # Config is fetched in load, not get_status
    assert manager.embed == mock_embed_instance
    assert manager.embed.get_embed_config().db_dir == str(tmp_path)
