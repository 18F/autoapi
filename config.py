import os

BUCKET_NAME = os.environ.get('AUTOAPI_BUCKET')
SQLA_URI = os.getenv(
    'AUTOAPI_SQLA_URI',
    ''.join(['sqlite:///', os.path.dirname(__file__), '/autoapi.sqlite']),
)
