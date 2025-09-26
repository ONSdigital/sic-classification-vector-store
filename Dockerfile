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

    # ARG _SIC_INDEX_FILE_URL=""
    ARG _SIC_INDEX_FILE_PATH=""
    ARG _SIC_INDEX_FILE=""


    WORKDIR /gcp_data
    
    RUN if [ -f "${_SIC_INDEX_FILE_PATH}" ]; then \
            # gsutil cp ${_SIC_INDEX_URL} ./SIC_index.xlsx
            cp "${_SIC_INDEX_FILE_PATH}" ./SIC_index.xlsx; \
        else \
            echo "File does not exist"; \
        fi

    # ---------- Stage 2: Build Application Image ----------
    FROM python:3.12-slim
    
    RUN if [ -f "${_SIC_INDEX_FILE_PATH}" ]; then \
            _SIC_INDEX_FILE="SIC_index.xlsx"; \
        else \
            echo "Using default SIC index"; \
        fi

    # Set env vars
    ENV POETRY_VERSION=2.1.1 \
        POETRY_HOME="/opt/poetry" \
        PATH="/opt/poetry/bin:$PATH" \
        PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1 \
        HF_HOME="/app/models" \
        SIC_INDEX_FILE="SIC_index.xlsx"
    
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
    
    # Copy application code
    COPY src/sic_classification_vector_store/ ./sic_classification_vector_store/
    
    # Copy predownloaded HF model
    COPY --from=model-downloader /models /app/models
    # Attempt to copy predownloaded extended SIC index file
    COPY --from=gcp-downloader /gcp_data/SIC_index.xlsx? /app/sic_classification_vector_store/data/sic_index/

    RUN if [ ! -f /app/sic_classification_vector_store/data/sic_index/ ]; then \
            cp /app/sic_classification_vector_store/data/sic_index/uksic2007indexeswithaddendumdecember2022.xlsx /app/sic_classification_vector_store/data/sic_index/SIC_index.xlsx; \
        fi
    
    # Ensure vector store directory is writable
    RUN mkdir -p ./sic_classification_vector_store/data/vector_store && \
        chown -R appuser:appuser /app
    
    # Drop to non-root user
    USER appuser
    
    EXPOSE 8088
    
    # Run the application
    CMD ["/opt/poetry/bin/poetry", "run", "uvicorn", "sic_classification_vector_store.api.main:app", "--host", "0.0.0.0", "--port", "8088"]