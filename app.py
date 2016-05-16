import os
import subprocess
from datetime import datetime

from flask import Flask, request
from flask.ext.basicauth import BasicAuth
from flask.ext.cors import CORS
from flask.views import View

import aws
import config
import sandman2
import swagger
import utils
from refresh_log import AutoapiTableRefreshLog as RefreshLog
from refresh_log import db as refresh_log_db


def make_app():
    app = sandman2.get_app(config.SQLA_URI, Base=utils.AutomapModel)

    app.json_encoder = utils.APIJSONEncoder
    app.config['CASE_INSENSITIVE'] = config.CASE_INSENSITIVE
    app.config['BASIC_AUTH_USERNAME'] = os.environ.get(
        'AUTOAPI_ADMIN_USERNAME', '')
    app.config['BASIC_AUTH_PASSWORD'] = os.environ.get(
        'AUTOAPI_ADMIN_PASSWORD', '')

    CORS(app)
    basic_auth = BasicAuth(app)

    @app.before_request
    def refresh():
        tables = utils.get_tables()
        if tables != app.config['SQLALCHEMY_TABLES']:
            utils.refresh_tables()
            app.config['SQLALCHEMY_TABLES'] = tables

    @app.before_request
    def protect_admin():
        if request.path.startswith('/admin/'):
            if not basic_auth.authenticate():
                return basic_auth.challenge()

    class RefreshTables(View):

        task_name = 'refresh'

        def dispatch_request(self):
            underway = RefreshLog.refresh_underway()
            if underway:
                return '''Refresh begun at {} still underway.

                Now: {}; timeout set for {} seconds'''.format(
                    underway.begun_at, datetime.now(),
                    config.REFRESH_TIMEOUT_SECONDS)
            try:
                subprocess.Popen(['invoke', self.task_name, ])
            except Exception as e:
                print('Problem with table refresh:')
                print(e)
            return 'Table refresh requested.'

    class QuickRefreshTables(RefreshTables):

        task_name = 'quick_refresh'

    app.add_url_rule('/refresh/', view_func=RefreshTables.as_view('refresh'))
    app.add_url_rule('/quick_refresh/', view_func=QuickRefreshTables.as_view('quick_refresh'))

    aws_blueprint = aws.make_blueprint()
    app.register_blueprint(aws_blueprint)

    docs_blueprint = swagger.make_blueprint(app)
    app.register_blueprint(docs_blueprint)

    with app.app_context():
        app.config['SQLALCHEMY_TABLES'] = utils.get_tables()
        utils.activate()

    refresh_log_db.init_app(app)
    refresh_log_db.create_all(app=app)

    return app
