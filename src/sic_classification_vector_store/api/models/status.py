"""This module contains the models for the status response.

The models in this module are used to represent the response
returned by the API.
"""

from industrial_classification_utils.models.config_model import EmbeddingConfig
from pydantic import model_validator


class StatusResponse(EmbeddingConfig):
    """Model representing the vector store status response.

    Attributes:
        embedding_model_name (str): The name of the embeddings model.
        db_dir (str): The vector store directory.
        index_source_file (str): The source file for the index.
        k_matches (int): The number of nearest matches initialised in the vector store.
        index_size (int): The number of embedded entries in the vector store.
        status (str): The status of the vector store.
    """

    status: str

    @model_validator(mode="after")
    def validate_ready_state(self) -> "StatusResponse":
        """Validate that required fields are present when the status is ready."""
        if self.status == "ready":
            if self.k_matches is None or self.k_matches < 1:
                raise ValueError("k_matches must be at least 1 when ready")
            if self.k_matches > 100:  # noqa: PLR2004
                raise ValueError("k_matches must be at most 100")
            if self.index_size is None or self.index_size < 1:
                raise ValueError("index_size must be at least 1 when ready")
            for field, val in [
                ("embedding_model_name", self.embedding_model_name),
                ("db_dir", self.db_dir),
                ("index_source_file", self.index_source_file),
            ]:
                if not val or val == "unknown":
                    raise ValueError(f"{field} must be a valid value when ready")
        return self
