"""Main entry point to the SIC Vector Store Backend API.

This module contains the main entry point to the API.
It defines the FastAPI application and the API endpoints.
"""

from contextlib import asynccontextmanager
from threading import Thread

from fastapi import FastAPI

from api.routes.v1.search_index import router as search_index_router
from api.routes.v1.status import router as status_router
from utils.vector_store import load_vector_store, vector_store_ready_event


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """FastAPI lifespan handler to load vector store in background."""

    def background_load():
        try:
            print("Loading the vector store")
            app.state.embed = load_vector_store()
            vector_store_ready_event.set()
            print("Vector store is ready")
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error loading vector store: {e}")

    # Start loading in a separate thread
    Thread(target=background_load, daemon=True).start()

    yield  # Let the app run

    # Placeholder for cleanup on shutdown if needed
    print("Shutting down...")


app: FastAPI = FastAPI(
    title="SIC Vector Store API",
    description="API for interacting with SIC Vector Store",
    version="1.0",
    lifespan=lifespan,
)

# Include versioned routes
app.include_router(status_router, prefix="/v1/sic-vector-store")
app.include_router(search_index_router, prefix="/v1/sic-vector-store")


@app.get("/")
def read_root() -> dict[str, str]:
    """Root endpoint for the API.

    Returns:
        dict: A dictionary with a message indicating the API is running.
    """
    return {"message": "SIC Vector Store API is running"}
