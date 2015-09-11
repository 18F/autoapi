import os

import sandman2

from flask import request
from flask.ext.cors import CORS
from flask.ext.basicauth import BasicAuth
from werkzeug.wsgi import DispatcherMiddleware

import aws
import utils
import config
import swagger

def make_app():
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

    aws_blueprint = aws.make_blueprint()
    app.register_blueprint(aws_blueprint)

    docs_blueprint = swagger.make_blueprint(app)
    app.register_blueprint(docs_blueprint)

    route = os.path.join('/api-program', config.API_NAME)
    container = DispatcherMiddleware(app.wsgi_app, {route: app})

    with app.app_context():
        app.config['SQLALCHEMY_TABLES'] = utils.get_tables()
        utils.activate()

    return app, container
