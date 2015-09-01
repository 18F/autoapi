Quickstart
----------

::

    pip install invoke
    invoke requirements
    export AWS_ACCESS_KEY_ID="..."
    export AWS_SECRET_ACCESS_KEY="..."
    export AUTOAPI_BUCKET="..."
    invoke serve

    curl http://localhost:5000
    curl http://localhost:5000/sample
    curl http://localhost:5000/sample/1
    curl http://localhost:5000/sample?LastName=SMITH

Database Configuration
----------------------

By default, autoapi uses a local SQLite database. To specify a different database URI, set the `DATABASE_URL` environment variable. For use with Cloud Foundry, simply create and bind an RDS service; this will automatically configure the environment.

::

    cf create-service rds shared-psql autoapi-rds
    cf bind-service autoapi autoapi-rds

Example Implementation 
----------------------

* https://autoapi.18f.gov/
* if you want to see json, you can `curl https://autoapi.18f.gov`
* https://autoapi.18f.gov/admin - `api-program` / `all-the-things`

AWS Integration
---------------

**autoapi** synchronizes with the S3 bucket specified in the `AUTOAPI_BUCKET` environment variable. On starting the API server, **autoapi** creates a subscription to the target bucket using Amazon SNS. When files are added to or deleted from the bucket, the corresponding endpoints will automatically be updated on the API.
