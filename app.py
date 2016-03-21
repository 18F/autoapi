import os

import sandman2

from flask import Flask, request
from flask.views import View
from flask.ext.cors import CORS
from flask.ext.basicauth import BasicAuth
from werkzeug.wsgi import DispatcherMiddleware

import aws
import utils
import config
import swagger

def refresh_tables():
    utils.refresh_tables()
    tables = utils.get_tables()
    app.config['SQLALCHEMY_TABLES'] = tables
    print('refresh_tables run')

def main_app():
    app = sandman2.get_app(config.SQLA_URI, Base=utils.AutomapModel)
    app.json_encoder = utils.APIJSONEncoder
    app.config['CASE_INSENSITIVE'] = config.CASE_INSENSITIVE
    app.config['BASIC_AUTH_USERNAME'] = os.environ.get('AUTOAPI_ADMIN_USERNAME', '')
    app.config['BASIC_AUTH_PASSWORD'] = os.environ.get('AUTOAPI_ADMIN_PASSWORD', '')

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
        def dispatch_request(self):
            aws.fetch_bucket()
            utils.refresh_tables()
            return 'Tables refreshed.'

    app.add_url_rule('/refresh/', view_func=RefreshTables.as_view('refresh'))

    aws_blueprint = aws.make_blueprint()
    app.register_blueprint(aws_blueprint)

    docs_blueprint = swagger.make_blueprint(app)
    app.register_blueprint(docs_blueprint)

    with app.app_context():
        app.config['SQLALCHEMY_TABLES'] = utils.get_tables()
        utils.activate()

    return app

data_refresh_request_listener_app = Flask('data_refresh_request_listener')

@data_refresh_request_listener_app.route('/')
def index():
    print('Refresh requested!')
    refresh_tables()
    return 'Refresh requested!'

def make_app():
    app = main_app()
    route = os.path.join('/api-program', config.API_NAME)
    container = DispatcherMiddleware(app.wsgi_app, {route: app,
      '/refresh': data_refresh_request_listener_app })

    return app, container
