import os
import logging
import functools
import concurrent.futures

from invoke import task, run
from flask import request
from flask.ext.cors import CORS
from flask.ext.basicauth import BasicAuth

import aws
import utils
import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@task
def requirements(upgrade=True):
    cmd = 'pip install -r requirements.txt'
    if upgrade:
        cmd += ' --upgrade'
    run(cmd)

@task
def apify(file_name, table_name=None, primary_name='id', insert=True):
    table_name = table_name or utils.get_name(file_name)
    logger.info('Importing {0} to table {1}'.format(file_name, table_name))
    cmd_csv = 'in2csv {0}'.format(file_name)
    cmd_sql = 'csvsql --db {0} --primary {1} --tables {2}'.format(
        config.SQLA_URI,
        primary_name,
        table_name,
    )
    if insert:
        cmd_sql += ' --insert'
    utils.drop_table(table_name)
    cmd = '{0} | {1}'.format(cmd_csv, cmd_sql)
    run(cmd)
    utils.activate(base=utils.ReadOnlyModel, browser=False, admin=False, reflect_all=True)

@task
def serve(host='0.0.0.0', port=5000, debug=False):
    from sandman import app
    from sandman.model import activate
    app.json_encoder = utils.APIJSONEncoder
    app.config['SERVER_PORT'] = port
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLA_URI
    app.config['BASIC_AUTH_USERNAME'] = os.environ.get('AUTOAPI_ADMIN_USERNAME', '')
    app.config['BASIC_AUTH_PASSWORD'] = os.environ.get('AUTOAPI_ADMIN_PASSWORD', '')

    CORS(app)
    basic_auth = BasicAuth(app)

    @app.before_request
    def protect_admin():
        if request.path.startswith('/admin/'):
            if not basic_auth.authenticate():
                return basic_auth.challenge()

    blueprint = aws.make_blueprint()
    app.register_blueprint(blueprint)

    # Load bucket in a separate process, then activate sandman in the main process
    with concurrent.futures.ProcessPoolExecutor() as pool:
        future = pool.submit(aws.fetch_bucket)
        callback = functools.partial(activate, base=utils.ReadOnlyModel, browser=False)
        future.add_done_callback(callback)

    app.run(host=host, port=port, debug=debug)
