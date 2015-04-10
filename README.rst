Quickstart
----------

::

    pip install invoke
    invoke requirements
    invoke apify sample.xlsx sqlite:///$(pwd)/autoapi.sqlite
    invoke serve sqlite:///$(pwd)/autoapi.sqlite

    curl http://localhost:5000
    curl http://localhost:5000/sample
    curl http://localhost:5000/sample/1
    curl http://localhost:5000/sample?LastName=SMITH
