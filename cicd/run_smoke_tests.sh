#!/bin/bash

# Wrapper script to run the smoke tests locally
#
# Expected Env variables: 
# SIC_VECTOR_STORE_URL - The URL of the SIC classification API to run the tests against
# SA_ID_TOKEN - A valid Google Identity Token generated from your credentials (assuming you're running locally) 
#

if [[ -z "${SIC_VECTOR_STORE_URL}" ]]; then
    echo Environment variable SIC_VECTOR_STORE_URL was not set, getting sandbox url from parameter store:
    SIC_VECTOR_STORE_URL=$(gcloud parametermanager parameters versions describe sandbox --parameter=infra-test-config --location=global --project ons-cicd-surveyassist --format=json | python3 -c "import sys, json; print(json.load(sys.stdin)['payload']['data'])" | base64 --decode | python3 -c "import sys, json; print(json.load(sys.stdin)['cr-sic-url'])")/v1/sic-vector-store
    export SIC_VECTOR_STORE_URL
    echo "$SIC_VECTOR_STORE_URL"
else
    echo Using SIC_VECTOR_STORE_URL="$SIC_VECTOR_STORE_URL"
fi
#
# Example way to set token after gcloud auth login
# export SA_ID_TOKEN=`gcloud auth print-identity-token`
if [[ -z "${SA_ID_TOKEN}" ]]; then
    echo Environment variable SA_ID_TOKEN was not set, getting a new identity token from local credentials, if authenticated.
    SA_ID_TOKEN=$(gcloud auth print-identity-token)   
    export SA_ID_TOKEN 
else
    echo Using currently set SA_ID_TOKEN. If this becomes stale, run export SA_ID_TOKEN=\`gcloud auth print-identity-token\`
fi
pytest -s