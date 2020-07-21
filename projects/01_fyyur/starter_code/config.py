import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
app = Flask(__name__)


# TODO IMPLEMENT DATABASE URL
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:1234@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
db=SQLAlchemy(app)
migrate = Migrate(app, db)
