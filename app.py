import logging
import os

from flask import Flask
from flask_migrate import Migrate

from library.models import db
from library.urls import app_urls
from library.utils import before_request


logging.basicConfig()
logging.root.setLevel(getattr(logging, os.getenv("LOG_LEVEL", "INFO")))

migrate = Migrate()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_object("config.Config")
        # app.config.from_pyfile("config.py")
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    logging.info(f"Flask App: The following configuration were loaded:: {app.config}")

    # Register Extentions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register URLs
    app_urls(app)

    # Register Middleware
    before_request(app)

    return app
