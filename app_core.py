# -*- coding: utf-8 -*-
from flask import Flask, g, request
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from celery import Celery
from flask_babelex import Babel

def make_celery(app2):
    celery = Celery(app2.import_name, backend=app.config['CELERY_RESULT_BACKEND'], broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app2.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask

    return celery

app = Flask(__name__)
app.config.from_object('settings')
UPLOAD_FOLDER = 'static/uploads/'
SPHINX_FOLDER = 'sphinx/_build/html/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SPHINX_FOLDER'] = SPHINX_FOLDER
db = SQLAlchemy(app)

OSRM_DRIVE_ADDRESS = 'http://0.0.0.0:5000'
OSRM_BIKE_ADDRESS = '0.0.0.0:9000/v1/bicycling'
OSRM_WALK_ADDRESS = '0.0.0.0:26464/v1/walking'
app.config['OSRM_DRIVE_ADDRESS'] = OSRM_DRIVE_ADDRESS
app.config['OSRM_BIKE_ADDRESS'] = OSRM_BIKE_ADDRESS
app.config['OSRM_WALK_ADDRESS'] = OSRM_WALK_ADDRESS

JS_OSRM_DRIVE_ADDRESS = 'http://172.121.100.105/osrm-driving/route/v1'
JS_OSRM_BIKE_ADDRESS = '0.0.0.0:9000/v1/bicycling'
JS_OSRM_WALK_ADDRESS = 'http://172.121.100.105/osrm-walking/route/v1'
app.config['JS_OSRM_DRIVE_ADDRESS'] = JS_OSRM_DRIVE_ADDRESS
app.config['JS_OSRM_BIKE_ADDRESS'] = JS_OSRM_BIKE_ADDRESS
app.config['JS_OSRM_WALK_ADDRESS'] = JS_OSRM_WALK_ADDRESS

babel = Babel(app)
app.config['DEFAULT_SERVER_HOST_ADDRESS'] = 'http://193.137.7.163'

app.config['CELERY_BROKER_URL'] = 'amqp://localhost:5672//'
app.config['CELERY_RESULT_BACKEND'] = 'redis://127.0.0.1:6379/0'

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.init_app(app)
login_manager.login_view = 'login'


# create celery object
celery = make_celery(app)

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(['en', 'pt'])

@app.before_request
def _before_request():
    g.user = current_user
    g.locale = get_locale()


import views, models
from my_function_osrm import *