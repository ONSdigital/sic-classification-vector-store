# SIC Classification Vector Store

This code is used to implement a stand-alone vector store that is used for similarity search for Standard Industrial Classification.  The code uses the sic-classification-utils embeddings functionality to load a vector store and wraps it with a private API so that client code can:

GET /status
Check the status of the vector store, returns status as "loading" or "ready".

POST /search-index
Perform similarity search on a provided industry_desc, job_title and job_description.

## API Documentation

To access the swagger documentation ensure the API is running and then in a browser navigate to the /docs url
(e.g 127.0.01:8080/docs)
