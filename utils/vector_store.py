"""Provides utilities for the vector store.

This module contains utility functions to manage the vector store interface.
"""

from threading import Event

from industrial_classification_utils.embed.embedding import (
    EmbeddingHandler,
    embedding_config,
)

# Shared variables and events
vector_store_ready_event = Event()
INDEX_FILE = "data/sic_index/uksic2007indexeswithaddendumdecember2022.xlsx"
STRUCTURE_FILE = "data/sic_index/publisheduksicsummaryofstructureworksheet.xlsx"
vector_store_status = embedding_config


def load_vector_store() -> EmbeddingHandler:
    """Load the vector store."""
    # Create the embeddings index
    print("Loading the vector store")
    embed = EmbeddingHandler(db_dir="data/vector_store")
    embed.embed_index(
        from_empty=False,
        sic_index_file=INDEX_FILE,
        sic_structure_file=STRUCTURE_FILE,
    )
    vector_store_status = (  # pylint: disable=redefined-outer-name
        embed.get_embed_config()
    )

    print(f"Vector store status: {vector_store_status}")
    print("Vector store loaded")
    return embed


# Create a simple manager class to maintain compatibility
class VectorStoreManager:
    """Manager class for the vector store.

    This class provides a simple interface to the vector store functionality.
    It maintains the state of the vector store and provides methods to interact with it.
    """

    def __init__(self):
        """Initialize the vector store manager."""
        self.ready_event = vector_store_ready_event
        self.status = vector_store_status
        self.embed = None

    def load(self):
        """Load the vector store and update its status."""
        self.embed = load_vector_store()
        self.status = self.embed.get_embed_config()

    def search_index_multi(self, query):
        """Search the vector store with multiple queries.

        Args:
            query: List of queries to search for

        Returns:
            List of search results
        """
        return self.embed.search_index_multi(query)


# Create singleton instance
vector_store_manager = VectorStoreManager()
