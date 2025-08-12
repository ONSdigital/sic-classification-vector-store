# SIC Classification Vector Store - GCP Deployment Guide

This guide covers the deployment of the SIC Classification Vector Store to Google Cloud Platform (GCP) using Cloud Run.

## Prerequisites

- Google Cloud CLI (`gcloud`) installed and authenticated
- Docker installed and running
- Access to the `survey-assist-sandbox` project
- Poetry for dependency management

## 1. Build Docker Container Locally

First, build the Docker container locally to verify it works:

```bash
# Ensure you're in the project directory
cd sic-classification-vector-store

# Build the container
docker build -t sic-classification-vector-store:latest .

# Check the image size (expect ~12GB due to ML dependencies)
docker images sic-classification-vector-store:latest
```

## 2. Push to Google Artifact Registry

### 2.1 Create Artifact Registry Repository (if not exists)

```bash
gcloud artifacts repositories create sic-classification-vector-store \
    --repository-format=docker \
    --location=europe-west2 \
    --project=survey-assist-sandbox
```

### 2.2 Tag and Push Image

```bash
# Tag the image for Artifact Registry
docker tag sic-classification-vector-store:latest \
    europe-west2-docker.pkg.dev/survey-assist-sandbox/sic-classification-vector-store/sic-classification-vector-store:latest

# Push to Artifact Registry
docker push europe-west2-docker.pkg.dev/survey-assist-sandbox/sic-classification-vector-store/sic-classification-vector-store:latest
```

## 3. Deploy to Cloud Run

### 3.1 Initial Deployment

```bash
gcloud run deploy sic-classification-vector-store \
    --image=europe-west2-docker.pkg.dev/survey-assist-sandbox/sic-classification-vector-store/sic-classification-vector-store:latest \
    --region=europe-west2 \
    --project=survey-assist-sandbox \
    --port=8088 \
    --memory=4Gi \
    --cpu=4 \
    --timeout=600 \
    --allow-unauthenticated
```

### 3.2 Critical: Configure Instance-Based Scaling

**IMPORTANT**: The SIC Classification Vector Store requires instance-based scaling to prevent CPU sleep during startup. Serverless scaling (Min: 0) will cause the vector store loading to hang.

After the initial deployment, you must manually configure the scaling in the Cloud Console:

1. Go to **Cloud Run** in the GCP Console
2. Select the **sic-classification-vector-store** service
3. Click **Edit and Deploy new revision**
4. Ensure **Instance-based** is selected (not Serverless)
5. Set **Min instances: 1** and **Max instances: 1**
6. Ensure **Second generation** is selected
7. Deploy the new revision

### 3.3 Verify Instance-Based Scaling

```bash
gcloud run services describe sic-classification-vector-store \
    --region=europe-west2 \
    --project=survey-assist-sandbox
```

**Expected Output:**
```
Scaling: Auto (Min: 1, Max: 1)
```

## 4. Service Configuration

### 4.1 Environment Variables

The service uses these environment variables:

- `VECTOR_STORE_DIR`: Path to vector store data (set automatically)
- `HF_HOME`: HuggingFace model cache directory

## 5. Testing the Deployment

### 5.1 Check Service Status

```bash
# Get the service URL
gcloud run services describe sic-classification-vector-store \
    --region=europe-west2 \
    --project=survey-assist-sandbox \
    --format="value(status.url)"
```

### 5.2 Test Health Endpoint

```bash
# Test the root endpoint
curl "https://[SERVICE_URL]/"

# Expected: {"message": "SIC Vector Store API is running"}
```

### 5.3 Test Status Endpoint

```bash
# Check if vector store is ready
curl "https://[SERVICE_URL]/v1/sic-vector-store/status"

# Expected: {"status": "ready", "matches": 20, "index_size": 16618}
```

### 5.4 Test Search Functionality

```bash
# Test SIC classification search
curl -X POST \
    -H "Content-Type: application/json" \
    -d '{
        "industry_descr": "electrical installation",
        "job_title": "Electrician",
        "job_description": "I install and maintain electrical systems and wiring"
    }' \
    "https://[SERVICE_URL]/v1/sic-vector-store/search-index"

# Expected: JSON response with SIC codes and similarity scores
```

## 6. Service Endpoints

### 6.1 Available Endpoints

- **GET** `/` - Health check
- **GET** `/v1/sic-vector-store/status` - Vector store status
- **POST** `/v1/sic-vector-store/search-index` - SIC classification search

### 6.2 Search Request Format

```json
{
    "industry_descr": "string",
    "job_title": "string", 
    "job_description": "string"
}
```

### 6.3 Search Response Format

```json
{
    "results": [
        {
            "distance": 0.0,
            "title": "string",
            "code": "string",
            "four_digit_code": "string",
            "two_digit_code": "string"
        }
    ]
}
```

## 7. Initial Startup Behavior

### 7.1 Vector Store Loading Process

1. **Model Download**: HuggingFace models are pre-downloaded in Docker build
2. **Vector Store Creation**: ChromaDB vector store initialized
3. **SIC Data Loading**: Excel files loaded and processed
4. **Embedding Generation**: Text embeddings created for all SIC entries
5. **Service Ready**: Status changes to "ready"

### 7.3 Monitoring Progress

```bash
# Watch the logs during startup
gcloud run services logs read sic-classification-vector-store \
    --region=europe-west2 \
    --project=survey-assist-sandbox \
    --limit=100
```

## 8. Updating Existing Images

### 8.1 Rebuild and Push

```bash
# Build new image
docker build -t sic-classification-vector-store:latest .

# Tag and push
docker tag sic-classification-vector-store:latest \
    europe-west2-docker.pkg.dev/survey-assist-sandbox/sic-classification-vector-store/sic-classification-vector-store:latest

docker push europe-west2-docker.pkg.dev/survey-assist-sandbox/sic-classification-vector-store/sic-classification-vector-store:latest
```

### 8.2 Deploy Update

```bash
gcloud run services update sic-classification-vector-store \
    --image=europe-west2-docker.pkg.dev/survey-assist-sandbox/sic-classification-vector-store/sic-classification-vector-store:latest \
    --region=europe-west2 \
    --project=survey-assist-sandbox
```

### 8.3 Log Analysis

```bash
# Get recent logs
gcloud run services logs read sic-classification-vector-store \
    --region=europe-west2 \
    --project=survey-assist-sandbox \
    --limit=100

# Filter for errors
gcloud run services logs read sic-classification-vector-store \
    --region=europe-west2 \
    --project=survey-assist-sandbox \
    --limit=100 | grep -i error
```
```bash
# View structured logs
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="sic-classification-vector-store"' \
    --project=survey-assist-sandbox \
    --limit=50
```
