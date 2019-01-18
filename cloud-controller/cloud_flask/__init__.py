import os

from flask import Flask

from . import api, user, db


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        AMAZON_CLIENT_ID='client_id',
        AMAZON_CLIENT_SECRET='client_secret',
        DATABASE=os.path.join(app.instance_path, 'cloud-controller.sqlite'),
    )
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    app.register_blueprint(user.bp)
    app.register_blueprint(api.bp)

    return app
