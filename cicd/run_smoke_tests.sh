#!/bin/bash

# Wrapper script to run the smoke tests locally
#
# Expected Env variables: 
# SIC_API_URL - The URL of the SIC classfication API to run the tests against
# SA_ID_TOKEN - A valid Google Identity Token generated from your credentials (assuming you're running locally) 
#

# Example for Sandbox: 
# export SIC_API_URL=https://sic-classification-vector-store-670504361336.europe-west2.run.app/v1/sic-vector-store
if [[ -z "${SIC_API_URL}" ]]; then
    echo Environment variable SIC_API_URL was not set, setting defualt to Sandbox API URL.
    export SIC_API_URL=https://sic-classification-vector-store-670504361336.europe-west2.run.app/v1/sic-vector-store
else
    echo Using SIC_API_URL=$SIC_API_URL
fi
#
# Example way to set token after gcloud auth login
# export SA_ID_TOKEN=`gcloud auth print-identity-token`
if [[ -z "${SA_ID_TOKEN}" ]]; then
    echo Environment variable SA_ID_TOKEN was not set, getting a new identity token from local credentials, if authenticated.
    export SA_ID_TOKEN=`gcloud auth print-identity-token`   
else
    echo Using currently set SA_ID_TOKEN. If this becomes stale, run export SA_ID_TOKEN=\`gcloud auth print-identity-token\`
fi
pytest -s