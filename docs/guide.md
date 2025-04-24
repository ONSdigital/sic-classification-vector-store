# SIC Classification Vector Store Guide

## Overview

The SIC Classification Vector Store is a FastAPI-based service that provides vector storage and similarity search capabilities for Standard Industrial Classification (SIC) codes. This guide provides detailed information about the service's features, setup, and usage.

## Architecture

The service is built using:
- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation and settings management
- **Sentence Transformers**: For generating embeddings
- **FAISS**: For efficient similarity search
- **Pandas**: For data processing and management

## API Endpoints

### Status Endpoint
- **Path**: `/v1/sic-vector-store/status`
- **Method**: GET
- **Description**: Returns the current status of the vector store including:
  - Service status ("ready" or "loading")
  - Embedding model name
  - LLM model name
  - Database directory
  - SIC index file paths
  - Number of matches configured
  - Index size

### Search Index Endpoint
- **Path**: `/v1/sic-vector-store/search-index`
- **Method**: POST
- **Description**: Performs similarity search on SIC code descriptions
- **Request Body**:
  ```json
  {
    "industry_descr": "string",
    "job_title": "string",
    "job_description": "string"
  }
  ```
- **Response**: Returns a list of similar SIC codes with:
  - Distance (similarity score)
  - Title (SIC description)
  - Code (full SIC code)
  - Four digit code
  - Two digit code

## Integration with Survey Assist API

The Vector Store Service integrates with the Survey Assist API to provide:
- Embedding-based similarity search for SIC code classification
- Real-time status monitoring
- Efficient vector storage and retrieval
- Asynchronous communication

## Documentation

### Interactive Documentation
The service provides two types of interactive documentation:
1. **Swagger UI** (`/docs`)
   - Interactive API testing
   - Request/response schemas
   - Example values
   - Try-it-out functionality

2. **ReDoc** (`/redoc`)
   - Alternative documentation view
   - Clean, readable format
   - Schema visualisation

You can access these interactive documentation tools by ensuring the service is running and then navigating to the `/docs` or `/redoc` URL in a browser (e.g., http://127.0.0.1:8088/docs).

### API Specification
The OpenAPI specification is available at `/openapi.json`

## Development

### Prerequisites
- Python 3.12
- Poetry for dependency management
- Access to SIC code data files
- Sufficient memory for vector storage

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/ONSdigital/sic-classification-vector-store.git
   cd sic-classification-vector-store
   poetry install
   ```

2. Start the service:
   ```bash
   make run-vector-store
   ```

3. Access the service:
   - Vector Store: http://localhost:8088
   - Documentation: http://localhost:8088/docs

### Testing
The project includes comprehensive test coverage:
- API endpoint tests
- Vector store functionality tests
- Error handling tests
- Integration tests

Tests can be run using:
```bash
make unit-tests  # Run unit tests with coverage for utils module
make api-tests   # Run API tests with coverage for api module
make all-tests   # Run all tests with coverage for the entire project
```

The tests include coverage requirements:
- Minimum 80% coverage for each module
- Coverage reports showing missing lines
- Separate coverage for API and utility modules

### Code Quality
Code quality is maintained through:
- Static type checking with mypy
- Linting with pylint and ruff
- Code formatting with black
- Security checking with bandit
- Documentation with mkdocs

## Error Handling

The service implements robust error handling:
- Validation errors for invalid requests
- Service unavailability errors
- Detailed error messages for debugging
- Proper HTTP status codes for different error scenarios

## Configuration

The service provides a configuration system that includes:
- Embedding model selection
- Database directory configuration
- SIC index file paths
- Search parameters

Configuration is managed through environment variables and configuration files.

## Security

The service is designed to be deployed with:
- API Gateway integration
- Secure data storage
- Environment-specific configurations
- Rate limiting

## Contributing

Please refer to the project's contribution guidelines for information on:
- Code style
- Testing requirements
- Documentation standards
- Pull request process
