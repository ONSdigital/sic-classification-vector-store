# SIC Classification Vector Store

A stand alone vector store used for SIC classification

## Overview

This code creates a vector store used for similarity search to help classify Standard Industrial Code

## Features

- Fast API with endpoints for embedding lookup and vector store status

## Prerequisites

Ensure you have the following installed on your local machine:

- [ ] Python 3.12 (Recommended: use `pyenv` to manage versions)
- [ ] `poetry` (for dependency management)
- [ ] Colima (if running locally with containers)
- [ ] Terraform (for infrastructure management)
- [ ] Google Cloud SDK (`gcloud`) with appropriate permissions

### Local Development Setup

The Makefile defines a set of commonly used commands and workflows.  Where possible use the files defined in the Makefile.

#### Clone the repository

```bash
git clone https://github.com/ONSdigital/sic-classification-vector-store.git
cd sic-classification-vector-store
```

#### Install Dependencies

```bash
poetry install
```

#### Run the Vector Store Locally

To run locally execute:

```bash
make run-vector-store
```

**Note:** The vector store embeddings can take a while (up to 10 minutes) to compute. The vector store will be ready to search when the /status API endpoint returns a status of "ready" and application logging will report "Vector store is ready".

### GCP Setup

Placeholder

### Code Quality

Code quality and static analysis will be enforced using isort, black, ruff, mypy and pylint. Security checking will be enhanced by running bandit.

To check the code quality, but only report any errors without auto-fix run:

```bash
make check-python-nofix
```

To check the code quality and automatically fix errors where possible run:

```bash
make check-python
```

### Documentation

Documentation is available in the docs folder and can be viewed using mkdocs

```bash
make run-docs
```

### Testing

Pytest is used for testing alongside pytest-cov for coverage testing.  [/tests/conftest.py](/tests/conftest.py) defines config used by the tests.

API testing is added to the [/tests/tests_api.py](./tests/tests_api.py)

```bash
make api-tests
```

Unit testing for utility functions can be run using:

```bash
make unit-tests
```

All tests can be run using

```bash
make all-tests
```

### Environment Variables

Placeholder
