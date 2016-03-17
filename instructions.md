Using
=====

```
git clone https://github.com/18F/autoapi.git
cd autoapi
export AUTOAPI_NAME`=(a unique identifier)
```

The remaining steps depend on where
your files and API server will 'live'.

<table>
  <tr>
    <th>Server at</th>
    <th>CSV at</th>
    <th>Directions</th>
  </tr>
  <tr>
    <td>
      local
    </td>
    <td>
      local
    </td>
    <td>
      <ol>
        <li>Set up <a href="#python-environment">Python environment</a></li>
        <li>`invoke apify my_table.csv`</li>                      
        <li>`invoke serve`</li>                                   
      </ol>
    </td>
  </tr>
  <tr>
    <td>
      local
    </td>
    <td>
      your S3 bucket
    </td>
    <td>
      <ol>
        <li>Set up <a href="#python-environment">Python environment</a></li>
        <li><a href="#s3-credentials">Get S3 credentials</a></li>
        <li><a href="#set-local-env">Set environment with S3 credentials</a></li>
        <li>`invoke serve`</li>
      </ol>
    </td>
  <tr>
    <td>
      cloud.gov
    </td>
    <td>
      cloud.gov
    </td>
    <td>
      <ol>
        <li><a href="#push-cloud-gov">Push your app to cloud.gov</a></li>
        <li><a href="#cloud-s3">Set up cloud.gov S3 bucket</a></li>
        <li>`cf restage $AUTOAPI_NAME`</li>
        <li><a href="#fill-cloud-s3">Place your files on S3 bucket</a></li>
        <li>Access at https://</li>
        <li><a href="#cloud-troubleshoot">cloud.gov troubleshooting</a></li>
      </ol>
    </td>
  </tr>
  <tr>
    <td>
      cloud.gov
    </td>
    <td>
      your S3 bucket
    </td>
    <td>
      <ol>
        <li><a href="#push-cloud-gov">Push your app to cloud.gov</a></li>
        <li><a href="#s3-credentials">Get S3 credentials</a></li>
        <li><a href="#set-cloud-env">Set cloud.gov environment</a></li>
        <li>`cf restage $AUTOAPI_NAME`</li>
        <li>Access at https://</li>
        <li><a href="#cloud-troubleshoot">cloud.gov troubleshooting</a></li>
      </ol>
    </td>
  </tr>
</table>

Instruction details
===================

<div id="python-environment"></div>

Set up local Python environment
-------------------------------

  <li>Follow [these instructions]() to

    <li>install `virtualenv`
    <li>create a `virtualenv`
    <li>activate the virtualenv in your session, and use that session for the remainder of these steps.
    <li>`pip install -r requirements.txt`

<div id="s3-credentials"></div>

Get S3 credentials
------------------

Only necessary if you want to use an AWS S3 bucket you set up yourself -
not to serve from local files, or from an S3 bucket set up through
cloud.gov.

  <li>In [Identity and Access Management](https://console.aws.amazon.com/iam),
create a user and assign a policy like "AmazonS3ReadOnlyAccess" to it.

  <li>For that user, create an access key and download its credentials.

<div id="set-local-env"></div>

Set local environment variables for S3
--------------------------------------

Using your [S3 credentials](#s3-credentials),

```export ACCESS_KEY_ID=(Access Key ID from IAM user)
export SECRET_ACCESS_KEY=(Secret Access Key from IAM user)
export AUTOAPI_BUCKET=(your s3 bucket name)```

<div id="push-cloud-gov"></div>

Push app to cloud.gov
---------------------

  <li>Follow [these instructions]() to

  a. Create a cloud.gov account
  a. Install the `cf` command-line tool
  a. `cf login`
  a. `cf target -o (your organization) -s (your workspace)`

  <li>Push the app to cloud.gov, and bind a database service to it:

```cf push $AUTOAPI_NAME
cf set-env $AUTOAPI_NAME AUTOAPI_NAME $AUTOAPI_NAME
cf create-service aws-rds shared-psql ${AUTOAPI_NAME}-db
cf bind-service $AUTOAPI_NAME ${AUTOAPI_NAME}-db```

<div id="cloud-troubleshoot"></div>

Troubleshooting cloud.gov
-------------------------

- `cf logs $AUTOAPI_NAME --recent`

- [cloud.gov docs](https://docs.cloud.gov/)

<div id="cloud-s3"></div>

Set up an S3 bucket on cloud.gov
--------------------------------

  <li>Arrange payment!  Cloud.gov doesn't have a free tier for S3.

  <li>```cf create-service s3 basic ${AUTOAPI_NAME}-s3
cf bind-service ${AUTOAPI_NAME} ${AUTOAPI_NAME}-s3```

<div id="fill-cloud-s3"></div>

Place your files in cloud.gov S3 bucket
---------------------------------------

TODO

<div id="set-cloud-env"></div>

Set cloud.gov environment for S3
--------------------------------

```cf set-env $AUTOAPI_NAME ACCESS_KEY_ID (Access Key ID from IAM user)
cf set-env $AUTOAPI_NAME SECRET_ACCESS_KEY (Secret Access Key from IAM user)
cf set-env $AUTOAPI_NAME AUTOAPI_BUCKET (your s3 bucket name)```

Notes
=====

- By default, when serving locally, relational forms of your spreadsheets will be stored in an
`autoapi.sqlite` SQLite3 database file (you can change this in `config.py`).
