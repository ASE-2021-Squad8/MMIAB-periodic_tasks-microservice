"""
Flask initialization
"""
import os

__version__ = "0.1"

import connexion
from flask_environments import Environments
import logging
from celery import Celery
from celery.schedules import crontab  # cronetab for lottery
from datetime import timedelta
from flask import Flask

db = None
debug_toolbar = None
redis_client = None
app = None
api_app = None
logger = None


def create_app():
    """
    This method create the Flask application.
    :return: Flask App Object
    """
    global db
    global app
    global api_app

    # first initialize the logger
    init_logger()

    # getting the flask app
    app = Flask(__name__)

    flask_env = os.getenv("FLASK_ENV", "None")
    if flask_env == "development":
        config_object = "config.DevConfig"
    elif flask_env == "testing":
        config_object = "config.TestConfig"
    elif flask_env == "production":  # pragma: no cover
        config_object = "config.ProdConfig"
    else:
        raise RuntimeError(  # pragma: no cover
            "%s is not recognized as valid app environment. You have to setup the environment!"
            % flask_env
        )

    # Load config
    env = Environments(app)
    env.from_object(config_object)

    return app


def init_logger():
    global logger
    """
    Initialize the internal application logger.
    :return: None
    """
    logger = logging.getLogger(__name__)
    from flask.logging import default_handler

    logger.addHandler(default_handler)


#   period tasks are tested functionally
def create_celery(flask_app):  # pragma: no cover
    # broker's url and storing results
    BACKEND = BROKER = "redis://redis:6379"

    celery = Celery(__name__, backend=BACKEND, broker=BROKER)
    # set timezone
    celery.conf.timezone = "UTC"
    # set up period task
    celery.conf.beat_schedule = {
        # for coping with faults during message delivery
        "check_message": {
            "task": "mib.tasks.periodic_task.check_messages",
            "schedule": timedelta(minutes=15),  # every 15 minutes
            "args": [False],  # test mode
        },
        # lottery game
        "lottery": {
            "task": "mib.tasks.periodic_task.lottery",
            "schedule": crontab(0, 0, day_of_month="1"),  # every 1st
            "args": [False],  # test mode
        },
    }
    return celery
