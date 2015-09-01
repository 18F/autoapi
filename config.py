import os
import json
import logging

logger = logging.getLogger(__name__)

def parse_bool(value, default=False):
    if isinstance(value, bool):
        return value
    parsed = json.loads(value.lower())
    if isinstance(parsed, bool):
        return parsed
    logger.warn('Value "{0}" cannot be coerced to boolean'.format(value))
    return default

BUCKET_NAME = os.environ.get('AUTOAPI_BUCKET')
API_NAME = os.environ.get('AUTOAPI_NAME', 'autoapi')
CASE_INSENSITIVE = parse_bool(os.environ.get('AUTOAPI_CASE_INSENSITIVE', True))
SQLA_URI = os.getenv(
    'DATABASE_URL',
    ''.join([
        'sqlite+pysqlite:///',
        os.path.dirname(__file__),
        '/autoapi.sqlite'
    ]),
)
