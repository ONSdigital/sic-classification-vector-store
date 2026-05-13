"""Main entry point to the SIC Vector Store Backend API.

This module contains the main entry point to the API.
It defines the FastAPI application and the API endpoints.
"""

from contextlib import asynccontextmanager
from threading import Thread

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from survey_assist_utils.logging import get_logger
from survey_assist_utils.logging.logging_utils import SurveyAssistLogger

from sic_classification_vector_store.api.routes.v1.sayt import router as sayt_router
from sic_classification_vector_store.api.routes.v1.search_index import (
    router as search_index_router,
)
from sic_classification_vector_store.api.routes.v1.status import router as status_router
from sic_classification_vector_store.utils.sayt import SaytManager
from sic_classification_vector_store.utils.vector_store import vector_store_manager

logger: SurveyAssistLogger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """FastAPI lifespan handler to load vector store in background."""
    sayt_manager: SaytManager = SaytManager()

    def background_load():
        try:
            logger.info("Loading the vector store")
            vector_store_manager.load()
            vector_store_manager.ready_event.set()
            # Ensure matches is > 0 when ready
            if vector_store_manager.status["matches"] == 0:
                vector_store_manager.status["matches"] = 1
            logger.info("Vector store is ready")
        except Exception as e:  # pylint: disable=broad-exception-caught
            vector_store_manager.load_error = str(e)
            logger.error("Error loading vector store", error_msg=str(e), exc_info=True)
            vector_store_manager.ready_event.set()  # Set event even on error to prevent hanging

    def background_load_sayt():
        try:
            logger.info("Loading the SIC SAYT suggester")
            sayt_manager.load()
            sayt_manager.ready_event.set()
            logger.info("SIC SAYT suggester is ready")
        except Exception as e:  # pylint: disable=broad-exception-caught
            sayt_manager.load_error = str(e)
            logger.error(
                "Error loading SIC SAYT suggester", error_msg=str(e), exc_info=True
            )
            sayt_manager.ready_event.set()

    # Start loading in a separate thread
    Thread(target=background_load, daemon=True).start()
    Thread(target=background_load_sayt, daemon=True).start()

    yield {"sayt_manager": sayt_manager}

    logger.info("Shutting down...")


app: FastAPI = FastAPI(
    title="SIC Vector Store API",
    description="API for interacting with SIC Vector Store",
    version="1.0",
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def generic_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Handle generic exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"},
    )


# Include versioned routes
app.include_router(status_router, prefix="/v1/sic-vector-store")
app.include_router(search_index_router, prefix="/v1/sic-vector-store")
app.include_router(sayt_router, prefix="/v1/sic-vector-store")


@app.get("/")
def read_root() -> dict[str, str]:
    """Root endpoint for the API.

    Returns:
        dict: A dictionary with a message indicating the API is running.
    """
    return {"message": "SIC Vector Store API is running"}
