"""Utilities for the SIC search-as-you-type suggester."""

import os
import time
from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path
from threading import Event

from industrial_classification_utils.sayt import SAYTSuggester
from survey_assist_utils.logging import get_logger
from survey_assist_utils.logging.logging_utils import SurveyAssistLogger

logger: SurveyAssistLogger = get_logger(__name__)


def resolve_sayt_data_path() -> str:
    """Resolve the CSV path used to build the SIC SAYT suggester."""
    env_path = os.getenv("SIC_LOOKUP_DATA_PATH")
    if env_path and env_path.strip():
        return env_path.strip()

    try:
        data_dir: Traversable = resources.files("industrial_classification.data")
        resolved_path: Traversable = data_dir / "example_sic_lookup_data.csv"
        logger.info("Using packaged SIC SAYT data", data_path=str(resolved_path))
        return str(resolved_path)
    except (ImportError, OSError) as e:
        fallback_path: str = (
            "/usr/local/lib/python3.12/site-packages/industrial_classification/data/example_sic_lookup_data.csv"
        )
        logger.warning(
            "Could not resolve packaged SIC SAYT data, using fallback",
            data_path=fallback_path,
            error=str(e),
        )
        return fallback_path


class SaytManager:
    """Manage lifecycle and access to the SIC SAYT suggester."""

    def __init__(self, data_path: str | None = None) -> None:
        """Initialise the SAYT manager."""
        self.ready_event = Event()
        self.suggester: SAYTSuggester | None = None
        self.load_error: str | None = None
        self.data_path: str = data_path or ""

    def load(self) -> None:
        """Build the underlying SAYT suggester."""
        self.load_error = None
        if not self.data_path:
            self.data_path = resolve_sayt_data_path()

        start_time = time.perf_counter()
        logger.info("Loading SIC SAYT suggester", data_path=self.data_path)
        self.suggester = SAYTSuggester.from_csv(
            self.data_path,
            search_text_col="description",
            display_text_col="description",
        )
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        logger.info(
            "Loaded SIC SAYT suggester",
            data_path=self.data_path,
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


def create_sayt_manager(data_path: str | Path | None = None) -> SaytManager:
    """Create a SAYT manager with optional preconfigured data path."""
    resolved_data_path: str | None = None if data_path is None else str(data_path)

    return SaytManager(data_path=resolved_data_path)
