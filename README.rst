Summary
-------

AutoAPI is a very simple, very scalable API engine that converts flat data files into a web service.  To add, edit, and remove data from the API, you just add, overwrite, or delete flat files from an s3 bucket.  

Example Instance
----------------

* https://autoapi.18f.gov/
* https://autoapi2.18f.gov

How to use:

* To see json, you can `curl https://autoapi.18f.gov`
* You can also use an API viewer like [Postman for Chrome](https://chrome.google.com/webstore/detail/postman/fhbjgbiflinjbdggehcddcbncdddomop?hl=en)

Query Parameters:  

* ?page=2
* ?[columnheader]=[value]



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

For details on RDS services available through 18F Cloud Foundry, see https://docs.cloud.gov/apps/databases/.

Example Implementation 
----------------------

* https://autoapi.18f.gov/
* if you want to see json, you can `curl https://autoapi.18f.gov`
* https://autoapi.18f.gov/admin 

AWS Integration
---------------

**autoapi** synchronizes with the S3 bucket specified in the `AUTOAPI_BUCKET` environment variable. On starting the API server, **autoapi** creates a subscription to the target bucket using Amazon SNS. When files are added to or deleted from the bucket, the corresponding endpoints will automatically be updated on the API.


Public domain
---------------

This project is in the worldwide `public domain <LICENSE.md>`_. As stated in `CONTRIBUTING <CONTRIBUTING.md>`_:

	This project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the `CC0 1.0 Universal public domain dedication <https://creativecommons.org/publicdomain/zero/1.0/>`_.
	
	All contributions to this project will be released under the CC0 dedication. By submitting a pull request, you are agreeing to comply with this waiver of copyright interest.
