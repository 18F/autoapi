import os
import logging
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
def apify(filename, tablename=None):
    tablename = tablename or utils.get_name(filename)
    logger.info('Importing {0} to table {1}'.format(filename, tablename))
    utils.drop_table(tablename)
    utils.load_table(filename, tablename)
    utils.index_table(tablename, config.CASE_INSENSITIVE)
    utils.activate(base=utils.ReadOnlyModel)
    logger.info('Finished importing {0}'.format(filename))

@task
def serve(host='0.0.0.0', port=5000, debug=False):
    from sandman import app
    app.json_encoder = utils.APIJSONEncoder
    app.config['SERVER_PORT'] = port
    app.config['CASE_INSENSITIVE'] = config.CASE_INSENSITIVE
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

    # Activate sandman with existing models
    utils.activate(admin=True)

    # Load bucket in a separate process, then re-activate sandman in the main process
    pool = concurrent.futures.ProcessPoolExecutor()
    future = pool.submit(aws.fetch_bucket)
    future.add_done_callback(utils.activate)
    pool.shutdown(wait=False)

    app.run(host=host, port=port, debug=debug)
