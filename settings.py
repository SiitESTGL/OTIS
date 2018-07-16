import os

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
DEBUG = True
DATABASE = 'db/default_db.db'
#DATABASE = 'db/douroapp_db.db'

#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db/douroapp_db.db')
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db/default_db.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True
