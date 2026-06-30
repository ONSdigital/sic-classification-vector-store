"""Build the vector store from the index source file.

This function checks for the presence of the INDEX_SOURCE_FILE environment variable
and builds the vector store using the EmbeddingHandler if it is set. If the variable is not set,
it logs a warning and skips the build process.
"""

import os

from industrial_classification_utils.embed import EmbeddingHandler
from survey_assist_utils.logging import get_logger

from time import perf_counter

EMBEDDING_BACKEND = os.getenv("EMBEDDING_BACKEND", None)
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", None)

logger = get_logger(__name__, level="DEBUG")


# Configuration from environment variables with defaults
VECTOR_STORE_DIR = os.getenv(
    "VECTOR_STORE_DIR", "src/sic_classification_vector_store/data/vector_store"
)
INDEX_SOURCE_FILE = os.getenv("INDEX_SOURCE_FILE", None)


def build_vector_store_index(db_dir: str,
                             index_source_file: str,
                             embedding_backend: str | None = None,
                             embedding_model_name: str | None = None) -> None:
    """Build the vector store from the given index source file.

    Args:
        db_dir: Directory to write the vector store into.
        index_source_file: Path to the CSV source file.
    """
    started = perf_counter()
    logger.info(f"Building vector store source={index_source_file} dir={db_dir} backend={embedding_backend} model={embedding_model_name}")
    EmbeddingHandler(db_dir=db_dir,
                     index_source_file=index_source_file,
                     embedding_backend=embedding_backend,
                     embedding_model_name=embedding_model_name)
    
    logger.info(f"Vector store built successfully dir={db_dir} source={index_source_file} backend={embedding_backend} model={embedding_model_name} in {perf_counter() - started:.2f}s")


if __name__ == "__main__":
    if not INDEX_SOURCE_FILE:
        logger.warning(
            "INDEX_SOURCE_FILE environment variable not set. Skipping build."
        )
    else:
        build_vector_store_index(
            db_dir=VECTOR_STORE_DIR,
            index_source_file=INDEX_SOURCE_FILE,
            embedding_backend=EMBEDDING_BACKEND,
            embedding_model_name=EMBEDDING_MODEL_NAME,
        )
