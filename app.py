import os

from sandman import app

from flask import request
from flask.ext.cors import CORS
from flask.ext.basicauth import BasicAuth

import aws
import utils
import config

def make_app():
    app.json_encoder = utils.APIJSONEncoder
    app.config['CASE_INSENSITIVE'] = config.CASE_INSENSITIVE
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLA_URI
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
    app.config['SQLALCHEMY_TABLES'] = utils.get_tables()

    @app.before_request
    def protect_admin():
        if request.path.startswith('/admin/'):
            if not basic_auth.authenticate():
                return basic_auth.challenge()

    blueprint = aws.make_blueprint()
    app.register_blueprint(blueprint)

    utils.activate(admin=True)

    return app
