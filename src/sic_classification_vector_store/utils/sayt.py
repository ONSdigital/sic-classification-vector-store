"""Utilities for the SIC search-as-you-type suggester."""

import os
import time
from collections.abc import Iterator
from contextlib import contextmanager
from importlib import resources
from threading import Event

from industrial_classification_utils.sayt import SAYTSuggester
from survey_assist_utils.logging import get_logger
from survey_assist_utils.logging.logging_utils import SurveyAssistLogger

logger: SurveyAssistLogger = get_logger(__name__)


class SaytManager:
    """Manage lifecycle and access to the SIC SAYT suggester."""

    def __init__(self, data_path: str | os.PathLike | None = None) -> None:
        """Initialise the SAYT manager."""
        self.ready_event = Event()
        self.suggester: SAYTSuggester | None = None
        self.load_error: str | None = None
        self.data_path: str | None = None if data_path is None else str(data_path)

    def load(self) -> None:
        """Build the underlying SAYT suggester."""
        self.load_error = None

        start_time = time.perf_counter()
        with _resolve_sayt_data_file(self.data_path) as resolved_path:
            active_data_path = str(resolved_path)
            logger.info("Loading SIC SAYT suggester", data_path=active_data_path)
            self.suggester = SAYTSuggester.from_csv(
                resolved_path,
                search_text_col="description",
                display_text_col="description",
            )

        duration_ms = int((time.perf_counter() - start_time) * 1000)
        logger.info(
            "Loaded SIC SAYT suggester",
            data_path=active_data_path,
            duration_ms=str(duration_ms),
        )

    def suggest(
        self, description: str | None, num_suggestions: int | None = None
    ) -> list[str]:
        """Return suggestions from the warmed SAYT suggester."""
        if self.load_error is not None:
            raise RuntimeError(f"SAYT suggester failed to load: {self.load_error}")

        if not self.ready_event.is_set():
            raise RuntimeError("SAYT suggester is not ready")

        if self.suggester is None:
            raise RuntimeError("SAYT suggester not loaded")

        return self.suggester.suggest(description, num_suggestions)


@contextmanager
def _resolve_sayt_data_file(
    data_path: str | os.PathLike | None,
) -> Iterator[str | os.PathLike]:
    """Yield a concrete CSV path for loading the SIC SAYT suggester."""
    if data_path is not None:
        yield data_path
        return

    env_path = os.getenv("SIC_LOOKUP_DATA_PATH")
    if env_path and env_path.strip():
        yield env_path.strip()
        return

    try:
        packaged_data = (
            resources.files("industrial_classification.data")
            / "example_sic_lookup_data.csv"
        )
    except (ImportError, OSError) as e:
        message = (
            "Could not resolve packaged SIC SAYT data. "
            "Set SIC_LOOKUP_DATA_PATH to override the CSV path."
        )
        logger.warning(message, error=str(e))
        raise RuntimeError(message) from e

    if not packaged_data.is_file():
        message = (
            "Packaged SIC SAYT data not found. "
            "Set SIC_LOOKUP_DATA_PATH to override the CSV path."
        )
        logger.warning(message, data_path=str(packaged_data))
        raise RuntimeError(message)

    logger.info("Using packaged SIC SAYT data", data_path=str(packaged_data))
    with resources.as_file(packaged_data) as resolved_path:
        yield resolved_path
