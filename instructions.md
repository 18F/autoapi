
Get this code  
=============


1. [clone this repository]()

1. `cd autoapi`

1. Follow directions below to run either locally or from cloud.gov.

1. `set AUTOAPI_NAME=(an identifier for your API)`

To run locally
==============

1. Follow [these instructions]() to

  1. install `virtualenv`
  1. create an "autoapi" `virtualenv`
  1. activate the autoapi virtualenv in your session, and use that session for the remainder of these steps.

1. `pip install -r requirements.txt`

TODO

To run from cloud.gov
=====================

1. Follow [these instructions]() to

  1. Create a cloud.gov account
  2. Install the `cf` command-line tool
  3. `cf login`
  4. `cf target -o (your organization) -s (your workspace)`

1. Choose a unique name for your application and `set` the `CF_APP_NAME` environment variable to it: `set CF_APP_NAME=sample-autoapi-app`

1. Push the app to cloud.gov, and bind a database service to it:

```cf push $CF_APP_NAME
cf set-env $CF_APP_NAME AUTOAPI_NAME $CF_APP_NAME
cf create-service aws-rds shared-psql ${CF_APP_NAME}-db
cf bind-service $CF_APP_NAME ${CF_APP_NAME}-db```

To use your own S3 bucket
-------------------------

1. In [Identity and Access Management](https://console.aws.amazon.com/iam),
create a user and assign a policy like "AmazonS3ReadOnlyAccess" to it.

1. For that user, create an access key and download its credentials.

1. Set environment variables on your app to
```cf set-env $CF_APP_NAME ACCESS_KEY_ID (Access Key ID from IAM user)
cf set-env $CF_APP_NAME SECRET_ACCESS_KEY (Secret Access Key from IAM user)
cf set-env $CF_APP_NAME AUTOAPI_BUCKET (your s3 bucket name)```

1. Skip to "Finally"

To use a cloud.gov-hosted S3 bucket
-----------------------------------

1. Arrange payment!  Cloud.gov doesn't have a free tier for S3.

1. ```cf create-service s3 basic ${CF_APP_NAME}-s3
cf bind-service ${CF_APP_NAME} ${CF_APP_NAME}-s3
```

1. Go on to "Finally"

Finally
-------

1. `cf restage`

1. Visit https://

1. If there are problems, `cf logs $CF_APP_NAME --recent` and see [cloud.gov docs]().
