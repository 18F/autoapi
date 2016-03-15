
Get this code  
=============

1. [clone this repository]()

1. `cd autoapi`

1. Follow directions below to run either locally or from cloud.gov.

1. `set AUTOAPI_NAME=(an identifier for your API)`

To get S3 credentials
=====================

Only necessary if you want to use an AWS S3 bucket you set up yourself -
not to serve from local files, or from an S3 bucket set up through
cloud.gov.

1. In [Identity and Access Management](https://console.aws.amazon.com/iam),
create a user and assign a policy like "AmazonS3ReadOnlyAccess" to it.

1. For that user, create an access key and download its credentials.

To run locally
==============

1. Follow [these instructions]() to

  1. install `virtualenv`
  1. create an "autoapi" `virtualenv`
  1. activate the autoapi virtualenv in your session, and use that session for the remainder of these steps.

1. By default, relational forms of your spreadsheets will be stored in an
`autoapi.sqlite` SQLite3 database file (you can change this in `config.py`).
You can populate this database from your spreadsheets by either:

  a. Importing spreadsheets you have local access to with `invoke apify <file_name>`
  a. Importing spreadsheets from an S3 bucket:

    - Get access credentials for your bucket (see above).
    - Use those credentials to set environment variables: `export AWS_ACCESS_KEY_ID=(something)`, `export AWS_SECRET_ACCESS_KEY=(something)`
    - `invoke fetch_bucket`

1. Choose a name and set it as an environment variable: `export AUTOAPI_NAME=(something)`

1. `invoke serve`

To run from cloud.gov
=====================

1. Follow [these instructions]() to

  1. Create a cloud.gov account
  2. Install the `cf` command-line tool
  3. `cf login`
  4. `cf target -o (your organization) -s (your workspace)`

1. Choose a unique name for your application and `set` the `CF_APP_NAME` environment variable to it: `export CF_APP_NAME=sample-autoapi-app`

1. Push the app to cloud.gov, and bind a database service to it:

```cf push $CF_APP_NAME
cf set-env $CF_APP_NAME AUTOAPI_NAME $CF_APP_NAME
cf create-service aws-rds shared-psql ${CF_APP_NAME}-db
cf bind-service $CF_APP_NAME ${CF_APP_NAME}-db```

To use your own S3 bucket
-------------------------

1. Get your S3 credentials (see above)

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

1. `cf restage $CF_APP_NAME`

1. Visit https://

1. If there are problems, `cf logs $CF_APP_NAME --recent` and see [cloud.gov docs]().
