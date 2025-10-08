# ---------- Stage 1: Download HuggingFace model ----------
    FROM python:3.12-slim AS model-downloader

    # Set env vars
    ENV HF_HOME="/models"
    
    # Install minimal dependencies to download model
    RUN apt-get update && \
        apt-get install -y --no-install-recommends \
            build-essential \
            curl && \
        pip install --no-cache-dir sentence-transformers && \
        python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')" && \
        apt-get purge -y curl && \
        apt-get clean && rm -rf /var/lib/apt/lists/*
    
    # Doing SIC data transfer in form of a mock template with google SDK commented to introduce at a later date when used in CloudBuild:
    FROM google/cloud-sdk:slim AS gcp-downloader
    
    ARG _SIC_INDEX_FILE_PATH=""

    WORKDIR /gcp_data
    
    # If _SIC_INDEX_FILE_PATH is provided and not empty, copy it from the build context.
    # The Dockerfile frontend will skip this if the source path doesn't exist.
    COPY --chown=1001:1001 [ "${_SIC_INDEX_FILE_PATH}", "./extended_sic_index.xlsx" ]

    # ---------- Stage 2: Build Application Image ----------
    FROM python:3.12-slim

    # Set env vars
    ENV POETRY_VERSION=2.1.1 \
        POETRY_HOME="/opt/poetry" \
        PATH="/opt/poetry/bin:$PATH" \
        PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1 \
        HF_HOME="/app/models" 
    
    # Install Poetry and minimal build tools
    RUN apt-get update && \
        apt-get install -y --no-install-recommends \
            curl \
            build-essential \
            && curl -sSL https://install.python-poetry.org | python3 - && \
        apt-get purge -y curl && \
        apt-get clean && rm -rf /var/lib/apt/lists/*
    
    # Create non-root user
    RUN groupadd --gid 1001 appuser && \
        useradd --uid 1001 --gid appuser --shell /bin/bash --create-home appuser
    
    WORKDIR /app
    
    # Copy dependency files first for better layer caching
    COPY pyproject.toml ./
    COPY poetry.lock ./
    
    # Install only main (non-dev) dependencies
    RUN /opt/poetry/bin/poetry config virtualenvs.create false && \
    /opt/poetry/bin/poetry install --no-root --only main
    
    # Re-declare the ARG to make it available in this stage.
    ARG _SIC_INDEX_FILE_PATH
    # If the build-arg is provided, set the ENV var for the final image.
    
    # Copy application code
    COPY src/sic_classification_vector_store/ ./sic_classification_vector_store/
    COPY docker_entrypoint.sh /app/docker_entrypoint.sh

    # Copy predownloaded HF model
    COPY --from=model-downloader /models /app/models
    
    # Ensure vector store directory is writable
    RUN mkdir -p ./sic_classification_vector_store/data/vector_store && \
        chown -R appuser:appuser /app

    RUN chmod +x /app/docker_entrypoint.sh

    # Attempt to copy predownloaded extended SIC index file
    COPY --from=gcp-downloader /gcp_data/ /app/sic_classification_vector_store/data/sic_index/
    
    # Drop to non-root user
    USER appuser
    
    EXPOSE 8088
    # Set the docker_entrypoint to run the vector store service
    ENTRYPOINT ["/app/docker_entrypoint.sh", "${_SIC_INDEX_FILE_PATH}"]
