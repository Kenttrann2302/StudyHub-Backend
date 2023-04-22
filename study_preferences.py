# THIS IS REST API FOR CRUD METHODS FOR STUDY PREFERENCES DATA
# import libraries
import json
import pdb
from http import HTTPStatus
from werkzeug.exceptions import Conflict

import jwt
from flask import Flask, Response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Resource, inputs, reqparse, fields, marshal_with, abort
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector

# import other files in the root directory
from database.users_models import StudyPreferences, db
from get_env import (
    database_host,
    database_name,
    database_password,
    database_port,
    database_type,
    database_username,
    secret_key
)
from helper_functions.middleware_functions import token_required

# create an application to initialize the session with the database
study_pref_app = Flask(__name__)

# migration config
migrate = Migrate(study_pref_app, db)

# connect flask to postgres database using SQLALCHEMY
study_pref_app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"{database_type}://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}"
engine = create_engine(f"{database_type}://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}")
inspector = Inspector.from_engine(engine)

# Create the SQLAlchemy database object
db.init_app(study_pref_app)

# resources fields to serialize the response object
_study_preferences_resource_fields = {
    "user_id" : fields.String,
    "study_env_preferences" : fields.String,
    "study_time_preferences" : fields.String,
    "time_management_preferences" : fields.String,
    "study_techniques_preferences" : fields.String,
    "courses_preferences" : fields.String,
    "communication_preferences" : fields.String
}

# Querying and inserting into

