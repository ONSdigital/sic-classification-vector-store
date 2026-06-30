"""Provides utilities for the vector store.

This module contains utility functions to manage the vector store interface.
"""

import os
from threading import Event

from industrial_classification_utils.embed import (
    EmbeddingHandler,
    SearchIndexResponse,
)
from survey_assist_utils.logging import get_logger
from time import perf_counter

EMBEDDING_BACKEND = os.getenv("EMBEDDING_BACKEND", None)
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", None)

logger = get_logger(__name__, level="DEBUG")

# Shared variables and events
vector_store_ready_event = Event()

# Configuration from environment variables with defaults
VECTOR_STORE_DIR = os.getenv(
    "VECTOR_STORE_DIR", "src/sic_classification_vector_store/data/vector_store"
)


class VectorStoreManager:
    """Manager class for the vector store.

    This class provides a simple interface to the vector store functionality.
    It maintains the state of the vector store and provides methods to interact with it.
    """

    def __init__(self):
        """Initialise the vector store manager."""
        self.ready_event = vector_store_ready_event
        self.embed = None
        self.load_error: str | None = None

    def load(self):
        """Load the vector store and update its status."""
        self.load_error = None
        started = perf_counter()
        logger.info(f"Loading the vector store - db_dir: {VECTOR_STORE_DIR} backend: {EMBEDDING_BACKEND} model: {EMBEDDING_MODEL_NAME}")

        self.embed = EmbeddingHandler(
            db_dir=VECTOR_STORE_DIR,
            embedding_backend=EMBEDDING_BACKEND,
            embedding_model_name=EMBEDDING_MODEL_NAME
        )
        logger.info(f"Vector store loaded in {perf_counter() - started:.2f}s")

    def search(
        self, industry_descr: str = "", job_title: str = "", job_description: str = ""
    ) -> SearchIndexResponse:
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
