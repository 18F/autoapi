Using
=====

    git clone https://github.com/18F/autoapi.git
    cd autoapi
    export AUTOAPI_NAME=(a unique identifier)

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
      local (via Docker)
    </td>
    <td>
      local and/or S3
    </td>
    <td>
      <ol>
        <li>Install Docker (through <a href="https://kitematic.com/">Kitematic</a>,
          <a href="https://beta.docker.com/">Docker Beta</a>, or a
          Linux package manager)
           </li>
        <li>
          Place spreadsheet files in a <code>source_data</code> folder or on S3
        </li>
        <li>
          If using S3, <a href="#set-local-env">set environment with S3 credentials</a>
        </li>                      
        <li>Use <code>docker-machine ip</code> to get your Docker machine's IP address</li>
        <li>From the parent directory to `source_data`,
          <code><pre>
          docker run \
            -p 5000:5000 \
            -e "AUTOAPI_NAME=$AUTOAPI_NAME" \
            -e "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID" \
            -e "AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY" \
            -e "AUTOAPI_BUCKET=$AUTOAPI_BUCKET" \
            -v `pwd`/data_sources:/data_sources \
            --rm -it 18fgsa/autoapi
            </pre></code>
            (The repo contains this as a <code>run_docker.sh</code> script)
          </li>                                   
        <li>View page at IP address from <code>docker-machine</code>, typically http://192.168.99.100:5000</li>
      </ol>
    </td>
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
        <li>Set up <a href="#local-environment">local environment</a></li>
        <li><code>invoke apify my_table.csv</code></li>                      
        <li><code>invoke serve</code></li>                                   
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
        <li>Set up <a href="#local-environment">local environment</a></li>
        <li><a href="#s3-credentials">Get S3 credentials</a></li>
        <li><a href="#set-local-env">Set environment with S3 credentials</a></li>
        <li><code>invoke fetch_bucket </code></li>
        <li><code>invoke serve</code></li>
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
        <li><code>cf restage $AUTOAPI_NAME</code></li>
        <li><a href="#fill-cloud-s3">Place your files on S3 bucket</a></li>
        <li>Access at <code>https://AUTOAPI_NAME.apps.cloud.gov</code></li>
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
        <li><code>cf restage $AUTOAPI_NAME</code></li>
        <li>Access at <code>https://AUTOAPI_NAME.apps.cloud.gov</code></li>
        <li><a href="#cloud-troubleshoot">cloud.gov troubleshooting</a></li>
      </ol>
    </td>
  </tr>
</table>

Instruction details
===================

<div id="python-environment"></div>

Set up local environment
------------------------

1. Follow [these instructions]() to

    - install `virtualenv`

    - create a `virtualenv`

    - activate the virtualenv in your session, and use that session for the remainder of these steps.

    - `pip install -r requirements.txt`

2. Install Swagger static assets:

    ```
npm install
    ```

<div id="s3-credentials"></div>

Importing local files
---------------------

A table name differing from the filename can be specified:

    invoke apify <filename> <tablename>

`apify` supports wildcards - but only if `tablename` is *not* specified:

    invoke apify "allmydatafiles/*.*"

When wildcards are used, enclose the file path in quote marks - otherwise,
shell expansion will make the second filename look like a tablename and
confuse `apify`.

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

    export AWS_ACCESS_KEY_ID=(Access Key ID from IAM user)
    export AWS_SECRET_ACCESS_KEY=(Secret Access Key from IAM user)
    export AUTOAPI_BUCKET=(your s3 bucket name)

<div id="push-cloud-gov"></div>

Push app to cloud.gov
---------------------

1. Follow [these instructions](https://docs.cloud.gov/getting-started/accounts/) to

    1. Create a cloud.gov account
    1. Install the `cf` command-line tool
    1. `cf login`
    1. `cf target -o (your organization) -s (your workspace)`

1. Push the app to cloud.gov, and bind a database service to it:

    ```
    cf push $AUTOAPI_NAME
    cf set-env $AUTOAPI_NAME AUTOAPI_NAME $AUTOAPI_NAME
    cf create-service aws-rds shared-psql ${AUTOAPI_NAME}-db
    cf bind-service $AUTOAPI_NAME ${AUTOAPI_NAME}-db
    ```

<div id="cloud-troubleshoot"></div>

Troubleshooting cloud.gov
-------------------------

- `cf logs $AUTOAPI_NAME --recent`

- [cloud.gov docs](https://docs.cloud.gov/)

<div id="cloud-s3"></div>

Set up an S3 bucket on cloud.gov
--------------------------------

1. Arrange payment!  Cloud.gov doesn't have a free tier for S3.

1. Run:

    ```
cf create-service s3 basic ${AUTOAPI_NAME}-s3
cf bind-service ${AUTOAPI_NAME} ${AUTOAPI_NAME}-s3
    ```

<div id="fill-cloud-s3"></div>

Place your files in cloud.gov S3 bucket
---------------------------------------

You can transfer files to the bucket using a tool
like [Cyberduck](https://cyberduck.io/).  Your
bucket's name, set [above](#cloud-s3),
is ${AUTOAPI_NAME}-s3.
You will also need the Access Key ID and Secret Access Key,
which you can get from

    cf env $AUTOAPI_NAME

under `System-Provided:` \>
`VCAP_SERVICES` \> `s3` \> `credentials`, as `access_key_id`
and `secret_access_key`.

<div id="set-cloud-env"></div>

Set cloud.gov environment for S3
--------------------------------

    cf set-env $AWS_ACCESS_KEY_ID AWS_ACCESS_KEY_ID (Access Key ID from IAM user)
    cf set-env $AWS_SECRET_ACCESS_KEY AWS_SECRET_ACCESS_KEY (Secret Access Key from IAM user)
    cf set-env $AUTOAPI_NAME AUTOAPI_BUCKET (your s3 bucket name)

Refreshing data
===============

When the app is run locally, changes to the tables can be reflected
in the app by repeating `invoke apify` command and, if a table has
been deleted, by restarting the app.  

When the app is run on cloud.gov, visit the
`https://AUTOAPI_NAME.apps.cloud.gov/quick_refresh` endpoint to
load a new file from S3, or
`https://AUTOAPI_NAME.apps.cloud.gov/refresh` to incorporate all
changes in the files in S3 - including file deletions or changes
in the data in existing files.

The `autoapi_table_refresh_log` table is used to track the
progress of any refresh requests currently being handled.

Optional configuration
======================

- If your API will not be served from `https://api.18f.gov/(API name)`,

    ```
    export AUTOAPI_HOST=(actual hostname)
    cf set-env $AUTOAPI_NAME AUTOAPI_HOST $AUTOAPI_HOST
    ```

- The Swagger API interface offers the default API key of DEMO_KEY1 by default.  To change:

    ```
    export AUTOAPI_DEMO_KEY=(actual demo key)
    cf set-env $AUTOAPI_NAME AUTOAPI_DEMO_KEY $AUTOAPI_DEMO_KEY
    ```

- By default, an in-process refresh is abandoned after one hour.  To change (for example, to 10 minutes):

    ```
    export AUTOAPI_REFRESH_TIMEOUT_SECONDS=600
    cf set-env $AUTOAPI_NAME AUTOAPI_REFRESH_TIMEOUT_SECONDS $AUTOAPI_REFRESH_TIMEOUT_SECONDS
    ```

- By default, when serving locally, relational forms of your spreadsheets will be stored in an
`autoapi.sqlite` SQLite3 database file.  To change, supply an alternate valid [SQLAlchemy database URL](http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html); for example,

    ```
    export DATABASE_URL=postgresql://myusername:mypassword@localhost/apidb
    ```
