import os
import tempfile

import boto
import sqlalchemy as sa
from invoke import task, run
from flask import request
from flask.ext.basicauth import BasicAuth

EXTENSIONS = [
    '.csv',
    '.tsv',
    '.xlsx',
]

SQLA_URI = os.getenv(
    'AUTOAPI_SQLA_URI',
    ''.join(['sqlite:///', os.path.dirname(__file__), '/autoapi.sqlite']),
)

def _get_name(path):
    return os.path.splitext(os.path.split(path)[1])[0]

@task
def requirements(upgrade=True):
    cmd = 'pip install -r requirements.txt'
    if upgrade:
        cmd += ' --upgrade'
    run(cmd)

@task
def load_bucket(bucket_name, primary_name='id'):
    conn = boto.connect_s3()
    bucket = conn.get_bucket(bucket_name)
    keys = bucket.get_all_keys()
    for key in keys:
        name, ext = os.path.splitext(key.name)
        if ext not in EXTENSIONS:
            continue
        with tempfile.NamedTemporaryFile(suffix=ext) as temp:
            temp.write(key.get_contents_as_string())
            apify(temp.name, table_name=name, primary_name=primary_name)

@task
def apify(file_name, table_name=None, primary_name='id', insert=True):
    table_name = table_name or _get_name(file_name)
    cmd_csv = 'in2csv {0}'.format(file_name)
    cmd_sql = 'csvsql --db {0} --primary {1} --tables {2}'.format(
        SQLA_URI,
        primary_name,
        table_name,
    )
    if insert:
        cmd_sql += ' --insert'
    engine = sa.create_engine(SQLA_URI)
    metadata = sa.MetaData()
    try:
        table = sa.Table(table_name, metadata, autoload_with=engine)
        table.drop(engine)
    except sa.exc.NoSuchTableError:
        pass
    cmd = '{0} | {1}'.format(cmd_csv, cmd_sql)
    run(cmd)

@task
def serve(host='0.0.0.0', port=5000, debug=False):
    from sandman import app
    from sandman.model import activate
    import utils
    app.json_encoder = utils.APIJSONEncoder
    app.config['SERVER_PORT'] = port
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLA_URI
    app.config['BASIC_AUTH_USERNAME'] = os.environ.get('AUTOAPI_ADMIN_USERNAME', '')
    app.config['BASIC_AUTH_PASSWORD'] = os.environ.get('AUTOAPI_ADMIN_PASSWORD', '')
    activate()
    basic_auth = BasicAuth(app)
    @app.before_request
    def protect_admin():
        if request.path.startswith('/admin/'):
            if not basic_auth.authenticate():
                return basic_auth.challenge()
    basic_auth = BasicAuth(app)
    app.run(host=host, port=port, debug=debug)
