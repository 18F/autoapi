import json
import logging
import os

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
BASE_URL = os.environ.get('AUTOAPI_BASE_URL', 'https://autoapi.18f.gov')
API_HOST = os.environ.get('AUTOAPI_HOST', 'api.18f.gov')
if not API_HOST.endswith('/'):
    API_HOST = "{}/".format(API_HOST)
API_BASE_PATH = os.environ.get('AUTOAPI_BASE_PATH', '/')
CASE_INSENSITIVE = parse_bool(os.environ.get('AUTOAPI_CASE_INSENSITIVE', True))
REFRESH_TIMEOUT_SECONDS = int(os.environ.get('AUTOAPI_REFRESH_TIMEOUT_SECONDS',
                                             3600))
DEMO_KEY = os.environ.get('AUTOAPI_DEMO_KEY', 'DEMO_KEY1')

SQLA_URI = os.getenv(
    'DATABASE_URL',
    ''.join([
        'sqlite+pysqlite:///', os.path.dirname(__file__), '/autoapi.sqlite'
    ]), )
