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
