#!/bin/sh

if [ -n "$1" ]; then
  export SIC_INDEX_FILE="extended_sic_index.xlsx"
  echo "Using extended SIC index file"
fi

/opt/poetry/bin/poetry run uvicorn sic_classification_vector_store.api.main:app --host 0.0.0.0 --port 8088
