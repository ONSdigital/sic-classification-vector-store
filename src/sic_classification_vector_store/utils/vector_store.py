"""Provides utilities for the vector store.

This module contains utility functions to manage the vector store interface.
"""

import logging
import os
from threading import Event

from industrial_classification_utils.embed.embedding import (
    EmbeddingHandler,
    embedding_config,
)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Shared variables and events
vector_store_ready_event = Event()
vector_store_status = embedding_config

# Configuration from environment variables with defaults
VECTOR_STORE_DIR = os.getenv(
    "VECTOR_STORE_DIR", "src/sic_classification_vector_store/data/vector_store"
)
SIC_INDEX_FILE = os.getenv(
    "SIC_INDEX_FILE",
    "uksic2007indexeswithaddendumdecember2022.xlsx",
)
SIC_STRUCTURE_FILE = os.getenv(
    "SIC_STRUCTURE_FILE",
    "publisheduksicsummaryofstructureworksheet.xlsx",
)

# Reference paths for the index and structure files
PATH_REF = "sic_classification_vector_store.data.sic_index"
SIC_INDEX_TUPLE = (PATH_REF, SIC_INDEX_FILE)
SIC_STRUCTURE_TUPLE = (PATH_REF, SIC_STRUCTURE_FILE)


def load_vector_store() -> EmbeddingHandler:
    """Load the vector store."""
    # Create the embeddings index
    logger.info("Loading the vector store - db_dir: %s", VECTOR_STORE_DIR)
    embed = EmbeddingHandler(db_dir=VECTOR_STORE_DIR)

    logger.info("Loading the vector store - sic_index_file: %s", SIC_INDEX_TUPLE)
    logger.info(
        "Loading the vector store - sic_structure_file: %s", SIC_STRUCTURE_TUPLE
    )
    embed.embed_index(
        from_empty=False,
        sic_index_file=SIC_INDEX_TUPLE,
        sic_structure_file=SIC_STRUCTURE_TUPLE,
    )
    vector_store_status = (  # pylint: disable=redefined-outer-name
        embed.get_embed_config()
    )

    logger.info("Vector store status: %s", vector_store_status)
    logger.info("Vector store loaded")
    return embed


# Create a simple manager class to maintain compatibility
class VectorStoreManager:
    """Manager class for the vector store.

    This class provides a simple interface to the vector store functionality.
    It maintains the state of the vector store and provides methods to interact with it.
    """

    def __init__(self):
        """Initialise the vector store manager."""
        self.ready_event = vector_store_ready_event
        self.status = vector_store_status
        self.embed = None

    def load(self):
        """Load the vector store and update its status."""
        self.embed = load_vector_store()
        self.status = self.embed.get_embed_config()

    def search(
        self, industry_descr: str = "", job_title: str = "", job_description: str = ""
    ):
        """Search the vector store with the given parameters.

        Args:
            industry_descr: Industry description to search for
            job_title: Job title to search for
            job_description: Job description to search for

        Returns:
            List of search results

        Raises:
            RuntimeError: If the vector store is not ready
        """
        if not self.ready_event.is_set():
            raise RuntimeError("Vector store is not ready")

        if not self.embed:
            raise RuntimeError("Vector store not loaded")

        return self.embed.search_index_multi(
            query=[
                industry_descr or "",
                job_title or "",
                job_description or "",
            ]
        )


# Create singleton instance
vector_store_manager = VectorStoreManager()
