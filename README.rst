Summary
-------

AutoAPI is a very simple, very scalable API engine that converts flat data files into a web service.  To add, edit, and remove data from the API, you just add, overwrite, or delete flat CSV files from either an s3 bucket or your local filesystem.

Currently, AutoAPI is the core offering of the `18F API Program <https://pages.18f.gov/api-program/>`_, a comprehensive solution for government agencies to get up-and-running with production APIs quickly.


Example Instance
----------------

* https://autoapi.18f.gov/
* https://autoapi2.18f.gov

How to use:

* To see json, you can `curl https://autoapi.18f.gov`
* You can also use an API viewer like `Postman for Chrome <https://chrome.google.com/webstore/detail/postman/fhbjgbiflinjbdggehcddcbncdddomop?hl=en>`_

Query Parameters:

* ?page=2
* ?[columnheader]=[value]
* ?[columnheader1]=[value1]&[columnheader1]=[value2]  (returns results that have value1 OR value2)
* ?[columnheader1]=[value1]&[columnheader3]=[value4]  (returns results that have both value1 and value2)


Requirements
------------

In order to use autoapi, you'll need:

* Python 3.5
* npm

Alternatively, if you use Docker for development and/or deployment, you don't
need anything (except Docker, of course).


Quickstart
----------

First, let's get dependencies sorted out::

    pip3 install -r requirements.txt
    npm install

The easiest way to get started with autoapi is by serving CSV files from
your local filesystem.

Here's a quick way to generate some sample data::

    mkdir data_sources
    cat << EOF > data_sources/my_sample_data.csv
    name,color
    apple,red
    grapefruit,pink
    EOF

Now you can add your sample data to a local SQLite database::

    invoke apify "/data_sources/**.*"

Finally, you can start the server with::

    invoke serve

Now try visiting http://localhost:5000 in your browser, or poke at
the following URLs from the command-line::

    curl http://localhost:5000/my_sample_data
    curl http://localhost:5000/my_sample_data/1
    curl http://localhost:5000/my_sample_data?color=pink

More details can be found in `instructions.md <https://github.com/18F/autoapi/blob/master/instructions.md>`_.


Deployment via docker
---------------------

If you have `Docker <http://docker.io>`_ installed, you can run from a Docker
container with no further setup::

    docker run \
      -p 5000:5000 \
      -v `pwd`/data_sources:/data_sources \
      --rm -it 18fgsa/autoapi

Any environment variables can be set via the ``-e NAME=VALUE`` option.

Note that this sets up your autoapi instance by directly
pulling autoapi from its
`Docker Hub image <https://hub.docker.com/r/18fgsa/autoapi/>`_; it doesn't
even require you to clone autoapi's git repository. However, as a
result you won't be able to develop autoapi itself.


Development via docker
----------------------

If you'd like to use Docker for developing autoapi, just clone its
repository, build the docker image and start the server::

    docker-compose build
    docker-compose up

Now you can visit your server at http://localhost:5000.

If you want to set any environment variables, you can do so by creating
a ``.env`` file in the root directory of the repository, where each line
consists of a ``NAME=VALUE`` pair.

If any dependencies change, such as those listed in ``requirements.txt``
or ``package.json``, just re-run ``docker-compose build``.

For more information on using Docker for development, see the
`18F Docker Guide <https://pages.18f.gov/dev-environment-standardization/virtualization/docker/>`_.


Database Configuration
----------------------

By default, autoapi uses a local SQLite database. To specify a different database URI, set the ``DATABASE_URL`` environment variable. For use with Cloud Foundry, simply create and bind an RDS service; this will automatically configure the environment.

::

    cf create-service rds shared-psql autoapi-rds
    cf bind-service autoapi autoapi-rds

For details on RDS services available through 18F Cloud Foundry, see https://docs.cloud.gov/apps/databases/.


AWS Integration
---------------

To use AWS instead of local CSV files, you'll want to define the following
environment variables:

* ``AUTOAPI_BUCKET`` - The bucket containing your CSV files.
* ``AWS_ACCESS_KEY_ID`` - Your AWS access key.
* ``AWS_SECRET_ACCESS_KEY`` - Your AWS secret access key.

**autoapi** synchronizes with the S3 bucket specified in the ``AUTOAPI_BUCKET`` environment variable. On starting the API server, **autoapi** creates a subscription to the target bucket using Amazon SNS. When files are added to or deleted from the bucket, the corresponding endpoints will automatically be updated on the API.


Public domain
---------------

This project is in the worldwide `public domain <LICENSE.md>`_. As stated in `CONTRIBUTING <CONTRIBUTING.md>`_:

	This project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the `CC0 1.0 Universal public domain dedication <https://creativecommons.org/publicdomain/zero/1.0/>`_.

	All contributions to this project will be released under the CC0 dedication. By submitting a pull request, you are agreeing to comply with this waiver of copyright interest.
