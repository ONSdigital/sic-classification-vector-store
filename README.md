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

### Docker

To run the vector store in a container, first ensure colima is configured to have extra resources:

```bash
colima list
```

Colima requires at least 4 CPUs, 8GB of memory and 100GB of disk space to run. You can re-configure colima with the following command:

```bash
colima start --cpu 4 --memory 8 --disk 100
```

Build the docker image locally (note the vector store embeddings need to exist prior to building the image):

```bash
docker build -t vector-store -f Dockerfile .
```

or:

```bash
make docker-image
```

Run the image as a container locally:

```bash
docker run -p 8088:8088 vector-store
```

or:

```bash
make run-docker-image
```

### GCP Setup

The following instructions assume a Google account is available that has been configured to route requests via an application load balancer to this service which is going to be hosted in Cloud Run.  It is also assumed that the user in GCP has the appropriate permissions to push to artifact registry and deploy a cloud run service.

Instructions below use gcloud cli.

#### Publish Image in Artifact Registry

When you have built your docker image it needs to be tagged:

```bash
docker tag vector-store <region>-docker.pkg.dev/<GCP project name>/<repo>/vector-store:v0.0.1
```

Push the tagged image to the repository:

```bash
docker push <region>-docker.pkg.dev/<GCP project name>/<repo>/vector-store:v0.0.1
```

#### Deploy the Cloud Run Service

The following will limit traffic to the cloud run service from the load balancer only.  The vpc-connector allows the Cloud Run instance to access other GCP services or the internet using the private subnet.

```bash
gcloud run deploy vector-store \
--image=europe-west2-docker.pkg.dev/<GCP project name>/<repo>/vector-store:v0.0.1 \
--region=europe-west2 \
--vpc-connector=test-cloudrun-connector \
--vpc-egress=all \
--ingress=internal-and-cloud-load-balancing \
--port=8088 \
--memory 8Gi \
--cpu 4 \
--min-instances 1 \
--max-instances 1 \
--timeout 720
```

#### Update the Service to use Instance Based Allocation

**IMPORTANT** - this step is required otherwise the cloud run service will not be allocated the necessary CPU to build the vector store.  Instance based CLoud Run means the billing is for the lifetime of the instance, **this is suitable for testing only and costs should be monitored closely**.  Ensure the cloud run instance is deleted once you finish testing.

In the Google Cloud Console navigate to Cloud Run and select the service you deployed in the previous step.

Navigate to Edit and Deploy the Service and ensure that Billing is set to Instance-based and Execution environment is set to Second generation.

Select Deploy and monitor the logs, after two to three minute you will see a log like:

```bash
INFO:sic_classification_vector_store.api.main: Vector store is ready
```

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

#### Building or re-building the vector store

The vector store is built from a csv index file which is defined by the ```INDEX_SOURCE_FILE``` environment variable.  This should be set to a csv file with a header and at least two columns, one for the `label` and one for the `text` to be embedded.  The default file used in development is ```./data/example.csv```.

The created vector store is stored in the directory defined by the ```VECTOR_STORE_DIR``` environment variable.  By default this is set to ```./data/vector_store```.  When the vector store is built, a ```vectors.parquet``` and ```metadata.json``` file are created in this directory. These embeddings can then be uploaded to GCS and subsequent runs can load the pre-built store using the guidance below.

E.g:

```bash
export INDEX_SOURCE_FILE="gs://<bucket-name>/sic_vector_store_config/sic_extended_index_for_classifai.csv"
export VECTOR_STORE_DIR="src/sic_classification_vector_store/data/vector_store"
```

#### Loading a pre-built store

When the ```INDEX_SOURCE_FILE``` environment variable is not set, the vector store will attempt to load pre-built vector embeddings from ```VECTOR_STORE_DIR``` environment variable (this could be local or a GCS path).  

A ```vectors.parquet``` and ```metadata.json``` file must exist in the directory.

E.g:

```bash
export VECTOR_STORE_DIR="gs://<bucket-name>/sic_vector_store_config/vector_store"
```