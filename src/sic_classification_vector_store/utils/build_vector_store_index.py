"""Build the vector store from the index source file.

This function checks for the presence of the INDEX_SOURCE_FILE environment variable
and builds the vector store using the EmbeddingHandler if it is set. If the variable is not set,
it logs a warning and skips the build process.
"""

import os

from industrial_classification_utils.embed import EmbeddingHandler
from survey_assist_utils.logging import get_logger

logger = get_logger(__name__, level="DEBUG")


# Configuration from environment variables with defaults
VECTOR_STORE_DIR = os.getenv(
    "VECTOR_STORE_DIR", "src/sic_classification_vector_store/data/vector_store"
)
INDEX_SOURCE_FILE = os.getenv("INDEX_SOURCE_FILE", None)


def build_vector_store_index(db_dir: str, index_source_file: str) -> None:
    """Build the vector store from the given index source file.

    Args:
        db_dir: Directory to write the vector store into.
        index_source_file: Path to the CSV source file.
    """
    logger.info(f"Building vector store from index source file: {index_source_file}")
    EmbeddingHandler(db_dir=db_dir, index_source_file=index_source_file)
    logger.info(f"Vector store built successfully. Directory: {db_dir}")


if __name__ == "__main__":
    if not INDEX_SOURCE_FILE:
        logger.warning(
            "INDEX_SOURCE_FILE environment variable not set. Skipping build."
        )
    else:
        build_vector_store_index(
            db_dir=VECTOR_STORE_DIR, index_source_file=INDEX_SOURCE_FILE
        )
